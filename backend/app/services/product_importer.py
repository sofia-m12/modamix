import ipaddress
import http.client
import json
import socket
import ssl
import time
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse

from pydantic import AnyHttpUrl


class InvalidProductUrl(ValueError):
    pass


NON_PRODUCT_PATHS = {
    "account",
    "cart",
    "categories",
    "category",
    "collections",
    "collection",
    "pages",
    "search",
}
SOCIAL_HOST_SUFFIXES = (
    "facebook.com",
    "instagram.com",
    "linktr.ee",
    "tiktok.com",
)
STRUCTURED_PAGE = "structured_page"
MAX_PAGE_BYTES = 1_000_000
IMPORT_CACHE_TTL_SECONDS = 15 * 60
MAX_REDIRECTS = 3
IMPORT_CACHE: dict[str, tuple[float, dict[str, object]]] = {}


class JsonLdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.documents: list[str] = []
        self._inside_json_ld = False
        self._current_document: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._inside_json_ld = True
            self._current_document = []

    def handle_data(self, data: str) -> None:
        if self._inside_json_ld:
            self._current_document.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._inside_json_ld:
            self.documents.append("".join(self._current_document))
            self._inside_json_ld = False


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection that preserves TLS identity while pinning the TCP peer."""

    def __init__(self, hostname: str, address: str, port: int, timeout: float) -> None:
        super().__init__(hostname, port=port, timeout=timeout, context=ssl.create_default_context())
        self._address = address

    def connect(self) -> None:
        self.sock = socket.create_connection((self._address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)


def is_public_address(address: str) -> bool:
    return ipaddress.ip_address(address).is_global


def validate_direct_product_url(source_url: str | AnyHttpUrl) -> None:
    parsed_url = urlparse(str(source_url))
    hostname = parsed_url.hostname

    is_social_host = hostname is not None and any(
        hostname == suffix or hostname.endswith(f".{suffix}")
        for suffix in SOCIAL_HOST_SUFFIXES
    )
    if (
        parsed_url.scheme not in {"http", "https"}
        or hostname is None
        or hostname == "localhost"
        or parsed_url.username is not None
        or parsed_url.password is not None
        or is_social_host
    ):
        raise InvalidProductUrl("Submit a public direct product URL.")

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None

    if address is not None and not address.is_global:
        raise InvalidProductUrl("Submit a public direct product URL.")

    path_segments = [segment for segment in parsed_url.path.split("/") if segment]
    if not path_segments or path_segments[0].lower() in NON_PRODUCT_PATHS:
        raise InvalidProductUrl("Submit a public direct product URL.")


def resolve_host_addresses(hostname: str) -> list[str]:
    try:
        address_info = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as error:
        raise InvalidProductUrl("Submit a public direct product URL.") from error

    return list({item[4][0] for item in address_info})


def resolve_public_hostname(source_url: str | AnyHttpUrl) -> tuple[str, str]:
    hostname = urlparse(str(source_url)).hostname
    if hostname is None:
        raise InvalidProductUrl("Submit a public direct product URL.")

    resolved_addresses = resolve_host_addresses(hostname)
    if not resolved_addresses or not all(is_public_address(address) for address in resolved_addresses):
        raise InvalidProductUrl("Submit a public direct product URL.")
    return hostname, resolved_addresses[0]


def make_connection(parsed_url, hostname: str, address: str):
    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
    if parsed_url.scheme == "https":
        return PinnedHTTPSConnection(hostname, address, port, timeout=10)
    return http.client.HTTPConnection(address, port=port, timeout=10)


def fetch_page_html(source_url: str | AnyHttpUrl) -> str:
    current_url = str(source_url)
    for _ in range(MAX_REDIRECTS + 1):
        validate_direct_product_url(current_url)
        parsed_url = urlparse(current_url)
        hostname, address = resolve_public_hostname(current_url)
        connection = make_connection(parsed_url, hostname, address)
        target = parsed_url.path or "/"
        if parsed_url.query:
            target = f"{target}?{parsed_url.query}"
        host_header = hostname if parsed_url.port is None else f"{hostname}:{parsed_url.port}"

        try:
            connection.request(
                "GET",
                target,
                headers={"Host": host_header, "User-Agent": "ModaMix/0.1 product import"},
            )
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                response.read()
                if location is None:
                    raise OSError("Redirect response did not include a location.")
                current_url = urljoin(current_url, location)
                continue
            return response.read(MAX_PAGE_BYTES).decode("utf-8", errors="replace")
        finally:
            connection.close()

    raise OSError("Product URL redirected too many times.")


def find_product(document: Any) -> dict[str, Any] | None:
    if isinstance(document, list):
        for item in document:
            product = find_product(item)
            if product is not None:
                return product
        return None

    if not isinstance(document, dict):
        return None

    product_type = document.get("@type")
    if product_type == "Product" or (
        isinstance(product_type, list) and "Product" in product_type
    ):
        return document

    return find_product(document.get("@graph", []))


def extract_structured_product(page_html: str) -> dict[str, Any] | None:
    parser = JsonLdParser()
    parser.feed(page_html)

    for raw_document in parser.documents:
        try:
            document = json.loads(raw_document)
        except json.JSONDecodeError:
            continue

        product = find_product(document)
        if product is not None:
            return product

    return None


def normalize_images(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [image for image in value if isinstance(image, str)]
    return []


def normalize_offer(value: Any) -> dict[str, Any]:
    if isinstance(value, list):
        return next((offer for offer in value if isinstance(offer, dict)), {})
    return value if isinstance(value, dict) else {}


def import_product_page(source_url: AnyHttpUrl) -> dict[str, object]:
    validate_direct_product_url(source_url)
    cache_key = str(source_url)
    cached_import = IMPORT_CACHE.get(cache_key)
    if cached_import is not None and time.monotonic() - cached_import[0] < IMPORT_CACHE_TTL_SECONDS:
        return cached_import[1]

    try:
        page_html = fetch_page_html(source_url)
    except (http.client.HTTPException, ssl.SSLError, TimeoutError, OSError):
        return {
            "status": "failed",
            "product": {"source_url": str(source_url)},
        }

    product = extract_structured_product(page_html)
    if product is None:
        return {
            "status": "failed",
            "product": {"source_url": str(source_url)},
        }

    offer = normalize_offer(product.get("offers"))
    imported_product: dict[str, object] = {"source_url": str(source_url)}
    provenance: dict[str, str] = {}

    if isinstance(product.get("name"), str):
        imported_product["title"] = product["name"]
        provenance["title"] = STRUCTURED_PAGE

    images = normalize_images(product.get("image"))
    if images:
        imported_product["images"] = images
        provenance["images"] = STRUCTURED_PAGE

    if isinstance(offer.get("price"), (int, float, str)):
        imported_product["price"] = str(offer["price"])
        provenance["price"] = STRUCTURED_PAGE

    if isinstance(offer.get("priceCurrency"), str):
        imported_product["currency"] = offer["priceCurrency"]

    if provenance:
        imported_product["provenance"] = provenance

    required_fields = {"title", "images", "price", "currency"}
    status = "complete" if required_fields <= imported_product.keys() else "partial"
    completed_import = {"status": status, "product": imported_product}
    IMPORT_CACHE[cache_key] = (time.monotonic(), completed_import)
    return completed_import

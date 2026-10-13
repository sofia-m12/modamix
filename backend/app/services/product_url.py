import ipaddress
import socket
from typing import NoReturn
from urllib.parse import urlparse

from pydantic import AnyHttpUrl


class InvalidProductUrl(ValueError):
    pass


def raise_invalid_product_url(reason: str, cause: BaseException | None = None) -> NoReturn:
    error = InvalidProductUrl(reason)
    if cause is not None:
        raise error from cause
    raise error


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
AFFILIATE_HOST_SUFFIXES = (
    "liketk.it",
    "rstyle.me",
    "shop-links.co",
    "shopstyle.com",
)


def is_public_address(address: str) -> bool:
    return ipaddress.ip_address(address).is_global


def validate_direct_product_url(source_url: str | AnyHttpUrl) -> None:
    parsed_url = urlparse(str(source_url))
    hostname = parsed_url.hostname

    if parsed_url.scheme not in {"http", "https"}:
        raise_invalid_product_url("URL must use http or https.")
    if hostname is None:
        raise_invalid_product_url("URL must include a hostname.")
    if hostname == "localhost":
        raise_invalid_product_url("Localhost URLs are not allowed.")
    if parsed_url.username is not None or parsed_url.password is not None:
        raise_invalid_product_url("URLs with embedded credentials are not allowed.")
    if any(hostname == suffix or hostname.endswith(f".{suffix}") for suffix in SOCIAL_HOST_SUFFIXES):
        raise_invalid_product_url("Social media links are not supported; submit a direct product URL.")
    if any(hostname == suffix or hostname.endswith(f".{suffix}") for suffix in AFFILIATE_HOST_SUFFIXES):
        raise_invalid_product_url("Affiliate links are not supported; submit a direct product URL.")

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None

    if address is not None and not address.is_global:
        raise_invalid_product_url("Private or non-public IP addresses are not allowed.")

    path_segments = [segment for segment in parsed_url.path.split("/") if segment]
    if not path_segments or path_segments[0].lower() in NON_PRODUCT_PATHS:
        raise_invalid_product_url(
            "Submit a direct product page URL, not a category, search, or account page."
        )


def resolve_host_addresses(hostname: str) -> list[str]:
    try:
        address_info = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as error:
        raise_invalid_product_url("Could not resolve the product URL host.", error)

    return list({item[4][0] for item in address_info})


def resolve_public_hostname(source_url: str | AnyHttpUrl) -> tuple[str, str]:
    hostname = urlparse(str(source_url)).hostname
    if hostname is None:
        raise_invalid_product_url("URL must include a hostname.")

    resolved_addresses = resolve_host_addresses(hostname)
    if not resolved_addresses or not all(is_public_address(address) for address in resolved_addresses):
        raise_invalid_product_url("The product URL host does not resolve to a public address.")
    return hostname, resolved_addresses[0]

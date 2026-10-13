import http.client
import socket
import ssl
from urllib.parse import urljoin, urlparse

from pydantic import AnyHttpUrl

from app.services.product_url import resolve_public_hostname, validate_direct_product_url


MAX_PAGE_BYTES = 1_000_000
MAX_REDIRECTS = 3


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection that preserves TLS identity while pinning the TCP peer."""

    def __init__(self, hostname: str, address: str, port: int, timeout: float) -> None:
        super().__init__(hostname, port=port, timeout=timeout, context=ssl.create_default_context())
        self._address = address

    def connect(self) -> None:
        self.sock = socket.create_connection((self._address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)


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

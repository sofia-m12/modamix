import pytest

from app.services import product_url, retail_page


@pytest.mark.parametrize(
    ("source_url", "detail"),
    [
        ("http://127.0.0.1/products/jacket", "Private or non-public IP addresses are not allowed."),
        ("https://retailer.example/collections/jackets", "Submit a direct product page URL, not a category, search, or account page."),
        ("https://www.instagram.com/p/jacket-post/", "Social media links are not supported; submit a direct product URL."),
        ("https://rstyle.me/products/jacket", "Affiliate links are not supported; submit a direct product URL."),
    ],
)
def test_rejects_unsafe_or_non_product_urls(source_url: str, detail: str) -> None:
    with pytest.raises(product_url.InvalidProductUrl, match=detail):
        product_url.validate_direct_product_url(source_url)


def test_rejects_a_hostname_that_resolves_to_a_private_address(monkeypatch) -> None:
    monkeypatch.setattr(product_url, "resolve_host_addresses", lambda hostname: ["127.0.0.1"])

    with pytest.raises(product_url.InvalidProductUrl, match="does not resolve to a public address"):
        product_url.resolve_public_hostname("https://retailer.example/products/jacket")


def test_follows_a_safe_canonical_redirect(monkeypatch) -> None:
    class FakeResponse:
        def __init__(self, status: int, body: bytes = b"", location: str | None = None) -> None:
            self.status = status
            self.body = body
            self.location = location

        def getheader(self, name: str) -> str | None:
            return self.location if name == "Location" else None

        def read(self, size: int | None = None) -> bytes:
            return self.body

    class FakeConnection:
        def __init__(self, response: FakeResponse) -> None:
            self.response = response

        def request(self, method: str, target: str, headers: dict[str, str]) -> None:
            pass

        def getresponse(self) -> FakeResponse:
            return self.response

        def close(self) -> None:
            pass

    connections = [
        FakeConnection(FakeResponse(302, location="/products/cropped-utility-jacket")),
        FakeConnection(FakeResponse(200, body=b"<html>product</html>")),
    ]
    monkeypatch.setattr(
        retail_page,
        "resolve_public_hostname",
        lambda source_url: ("retailer.example", "203.0.113.25"),
    )
    monkeypatch.setattr(
        retail_page,
        "make_connection",
        lambda parsed_url, hostname, address: connections.pop(0),
    )

    assert retail_page.fetch_page_html("https://retailer.example/product/cropped-utility-jacket") == "<html>product</html>"


def test_rejects_an_unsafe_redirect_target(monkeypatch) -> None:
    class FakeResponse:
        status = 302

        def getheader(self, name: str) -> str | None:
            return "http://127.0.0.1/products/jacket" if name == "Location" else None

        def read(self, size: int | None = None) -> bytes:
            return b""

    class FakeConnection:
        def request(self, method: str, target: str, headers: dict[str, str]) -> None:
            pass

        def getresponse(self) -> FakeResponse:
            return FakeResponse()

        def close(self) -> None:
            pass

    monkeypatch.setattr(
        retail_page,
        "resolve_public_hostname",
        lambda source_url: ("retailer.example", "203.0.113.25"),
    )
    monkeypatch.setattr(
        retail_page,
        "make_connection",
        lambda parsed_url, hostname, address: FakeConnection(),
    )

    with pytest.raises(product_url.InvalidProductUrl):
        retail_page.fetch_page_html("https://retailer.example/product/cropped-utility-jacket")

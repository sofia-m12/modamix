from fastapi.testclient import TestClient
import pytest

from app.api.routes import imports
from app.main import app
from app.services import product_importer


@pytest.fixture(autouse=True)
def clear_import_cache() -> None:
    product_importer.IMPORT_CACHE.clear()


def test_imports_a_direct_product_url_as_a_reference_product(monkeypatch) -> None:
    monkeypatch.setattr(
        imports,
        "import_product_page",
        lambda source_url: {
            "status": "complete",
            "product": {
                "source_url": str(source_url),
                "title": "Cropped Utility Jacket",
                "images": ["https://retailer.example/images/jacket.jpg"],
                "price": "89.00",
                "currency": "USD",
                "provenance": {
                    "title": "structured_page",
                    "images": "structured_page",
                    "price": "structured_page",
                },
            },
        },
        raising=False,
    )

    response = TestClient(app).post(
        "/api/imports",
        json={"source_url": "https://retailer.example/products/cropped-utility-jacket"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "complete",
        "product": {
            "source_url": "https://retailer.example/products/cropped-utility-jacket",
            "title": "Cropped Utility Jacket",
            "images": ["https://retailer.example/images/jacket.jpg"],
            "price": "89.00",
            "currency": "USD",
            "provenance": {
                "title": "structured_page",
                "images": "structured_page",
                "price": "structured_page",
            },
        },
    }


@pytest.mark.parametrize(
    "source_url",
    [
        "http://127.0.0.1/products/jacket",
        "http://100.64.0.1/products/jacket",
        "https://retailer.example/collections/jackets",
        "https://retailer.example/search?q=jacket",
        "https://www.instagram.com/p/jacket-post/",
    ],
)
def test_rejects_unsafe_or_non_product_urls(source_url: str) -> None:
    response = TestClient(app).post("/api/imports", json={"source_url": source_url})

    assert response.status_code == 422
    assert response.json()["detail"] == "Submit a public direct product URL."


def test_rejects_a_product_url_that_resolves_to_a_private_address(monkeypatch) -> None:
    monkeypatch.setattr(
        product_importer,
        "resolve_host_addresses",
        lambda hostname: ["127.0.0.1"],
        raising=False,
    )

    response = TestClient(app).post(
        "/api/imports",
        json={"source_url": "https://retailer.example/products/cropped-utility-jacket"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Submit a public direct product URL."


def test_extracts_a_reference_product_from_structured_page_metadata(monkeypatch) -> None:
    monkeypatch.setattr(
        product_importer,
        "fetch_page_html",
        lambda source_url: """
        <html><head>
          <script type="application/ld+json">
            {
              "@context": "https://schema.org",
              "@type": "Product",
              "name": "Cropped Utility Jacket",
              "image": ["https://retailer.example/images/jacket.jpg"],
              "offers": {"@type": "Offer", "price": "89.00", "priceCurrency": "USD"}
            }
          </script>
        </head></html>
        """,
        raising=False,
    )

    response = TestClient(app).post(
        "/api/imports",
        json={"source_url": "https://retailer.example/products/cropped-utility-jacket"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "complete",
        "product": {
            "source_url": "https://retailer.example/products/cropped-utility-jacket",
            "title": "Cropped Utility Jacket",
            "images": ["https://retailer.example/images/jacket.jpg"],
            "price": "89.00",
            "currency": "USD",
            "provenance": {
                "title": "structured_page",
                "images": "structured_page",
                "price": "structured_page",
            },
        },
    }


def test_preserves_unknown_product_facts_in_a_partial_import(monkeypatch) -> None:
    monkeypatch.setattr(
        product_importer,
        "fetch_page_html",
        lambda source_url: """
        <script type="application/ld+json">
          {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Cropped Utility Jacket",
            "image": "https://retailer.example/images/jacket.jpg"
          }
        </script>
        """,
        raising=False,
    )

    response = TestClient(app).post(
        "/api/imports",
        json={"source_url": "https://retailer.example/products/cropped-utility-jacket"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "partial",
        "product": {
            "source_url": "https://retailer.example/products/cropped-utility-jacket",
            "title": "Cropped Utility Jacket",
            "images": ["https://retailer.example/images/jacket.jpg"],
            "provenance": {
                "title": "structured_page",
                "images": "structured_page",
            },
        },
    }


def test_caches_a_completed_import(monkeypatch) -> None:
    fetch_count = 0

    def fetch_page_html(source_url) -> str:
        nonlocal fetch_count
        fetch_count += 1
        return '''<script type="application/ld+json">{
          "@type": "Product", "name": "Cropped Utility Jacket",
          "image": "https://retailer.example/images/jacket.jpg"
        }</script>'''

    monkeypatch.setattr(product_importer, "fetch_page_html", fetch_page_html)
    source_url = "https://retailer.example/products/cropped-utility-jacket"

    first_response = TestClient(app).post("/api/imports", json={"source_url": source_url})
    second_response = TestClient(app).post("/api/imports", json={"source_url": source_url})

    assert first_response.json() == second_response.json()
    assert fetch_count == 1


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
            self.targets: list[str] = []

        def request(self, method: str, target: str, headers: dict[str, str]) -> None:
            self.targets.append(target)

        def getresponse(self) -> FakeResponse:
            return self.response

        def close(self) -> None:
            pass

    connections = [
        FakeConnection(FakeResponse(302, location="/products/cropped-utility-jacket")),
        FakeConnection(FakeResponse(200, body=b"<html>product</html>")),
    ]
    monkeypatch.setattr(
        product_importer,
        "resolve_public_hostname",
        lambda source_url: ("retailer.example", "203.0.113.25"),
    )
    monkeypatch.setattr(
        product_importer,
        "make_connection",
        lambda parsed_url, hostname, address: connections.pop(0),
    )

    page_html = product_importer.fetch_page_html("https://retailer.example/product/cropped-utility-jacket")

    assert page_html == "<html>product</html>"
    assert not connections


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
        product_importer,
        "resolve_public_hostname",
        lambda source_url: ("retailer.example", "203.0.113.25"),
    )
    monkeypatch.setattr(
        product_importer,
        "make_connection",
        lambda parsed_url, hostname, address: FakeConnection(),
    )

    with pytest.raises(product_importer.InvalidProductUrl):
        product_importer.fetch_page_html("https://retailer.example/product/cropped-utility-jacket")

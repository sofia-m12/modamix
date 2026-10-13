from fastapi.testclient import TestClient

from app.api.routes import imports
from app.main import app
from app.services import product_importer


def test_import_route_returns_a_reference_product(monkeypatch) -> None:
    monkeypatch.setattr(
        imports,
        "import_product_page",
        lambda source_url: {
            "status": "complete",
            "product": {"source_url": str(source_url), "title": "Cropped Utility Jacket"},
        },
    )

    response = TestClient(app).post(
        "/api/imports",
        json={"source_url": "https://retailer.example/products/cropped-utility-jacket"},
    )

    assert response.status_code == 200
    assert response.json()["product"]["title"] == "Cropped Utility Jacket"


def test_extracts_a_complete_import_from_structured_product_metadata(monkeypatch) -> None:
    monkeypatch.setattr(
        product_importer,
        "fetch_page_html",
        lambda source_url: '''<script type="application/ld+json">{
          "@type": "Product", "name": "Cropped Utility Jacket",
          "image": "https://retailer.example/images/jacket.jpg",
          "offers": {"price": "89.00", "priceCurrency": "USD"}
        }</script>''',
    )

    imported = product_importer.import_product_page(
        "https://retailer.example/products/cropped-utility-jacket"
    )

    assert imported["status"] == "complete"
    assert imported["product"]["provenance"] == {
        "title": "structured_page",
        "images": "structured_page",
        "price": "structured_page",
        "currency": "structured_page",
    }


def test_preserves_unknown_facts_in_a_partial_import(monkeypatch) -> None:
    monkeypatch.setattr(
        product_importer,
        "fetch_page_html",
        lambda source_url: '''<script type="application/ld+json">{
          "@type": "Product", "name": "Cropped Utility Jacket"
        }</script>''',
    )

    imported = product_importer.import_product_page(
        "https://retailer.example/products/partial-jacket"
    )

    assert imported["status"] == "partial"
    assert "price" not in imported["product"]
    assert "currency" not in imported["product"]


def test_returns_a_failed_import_when_product_metadata_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(product_importer, "fetch_page_html", lambda source_url: "<html></html>")

    imported = product_importer.import_product_page(
        "https://retailer.example/products/missing-metadata"
    )

    assert imported == {
        "status": "failed",
        "product": {"source_url": "https://retailer.example/products/missing-metadata"},
    }

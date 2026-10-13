import http.client
import ssl
import time
from dataclasses import dataclass

from pydantic import AnyHttpUrl

from app.services.product_url import InvalidProductUrl, validate_direct_product_url
from app.services.retail_page import fetch_page_html
from app.services.structured_product import (
    extract_structured_product,
    normalize_images,
    normalize_offer,
)


STRUCTURED_PAGE = "structured_page"
IMPORT_CACHE_TTL_SECONDS = 15 * 60


@dataclass
class CachedImport:
    saved_at: float
    response: dict[str, object]


IMPORT_CACHE: dict[str, CachedImport] = {}


def failed_import(source_url: str | AnyHttpUrl) -> dict[str, object]:
    return {
        "status": "failed",
        "product": {"source_url": str(source_url)},
    }


def import_product_page(source_url: AnyHttpUrl) -> dict[str, object]:
    validate_direct_product_url(source_url)
    cache_key = str(source_url)
    cached_import = IMPORT_CACHE.get(cache_key)
    if cached_import is not None and (
        time.monotonic() - cached_import.saved_at < IMPORT_CACHE_TTL_SECONDS
    ):
        return cached_import.response

    try:
        page_html = fetch_page_html(source_url)
    except (http.client.HTTPException, ssl.SSLError, TimeoutError, OSError):
        return failed_import(source_url)

    product = extract_structured_product(page_html)
    if product is None:
        return failed_import(source_url)

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
        provenance["currency"] = STRUCTURED_PAGE

    if provenance:
        imported_product["provenance"] = provenance

    required_fields = {"title", "images", "price", "currency"}
    status = "complete" if required_fields <= imported_product.keys() else "partial"
    completed_import = {"status": status, "product": imported_product}
    IMPORT_CACHE[cache_key] = CachedImport(
        saved_at=time.monotonic(),
        response=completed_import,
    )
    return completed_import

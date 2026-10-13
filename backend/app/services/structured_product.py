import json
from html.parser import HTMLParser
from typing import Any


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

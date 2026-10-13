from fastapi import APIRouter, HTTPException
from pydantic import AnyHttpUrl, BaseModel

from app.services.product_importer import InvalidProductUrl, import_product_page

router = APIRouter(prefix="/imports", tags=["imports"])


class ImportRequest(BaseModel):
    source_url: AnyHttpUrl


@router.post("")
def import_product(request: ImportRequest) -> dict[str, object]:
    try:
        return import_product_page(request.source_url)
    except InvalidProductUrl as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

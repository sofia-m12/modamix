from fastapi import APIRouter
from pydantic import AnyHttpUrl, BaseModel
router = APIRouter(prefix="/imports", tags=["imports"])
class ImportRequest(BaseModel):
    source_url: AnyHttpUrl
@router.post("")
def import_product(request: ImportRequest) -> dict[str, str]:
    return {"status": "queued", "source_url": str(request.source_url)}

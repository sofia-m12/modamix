from fastapi import APIRouter
from app.models.preferences import SearchPreferences
router = APIRouter(prefix="/searches", tags=["searches"])
@router.post("")
def search_products(preferences: SearchPreferences) -> dict[str, object]:
    return {"preferences": preferences.model_dump(), "results": []}

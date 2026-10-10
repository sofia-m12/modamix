from decimal import Decimal
from pydantic import BaseModel, Field
class SearchPreferences(BaseModel):
    category: str = "jacket"
    required_features: list[str] = Field(default_factory=list)
    preferred_features: list[str] = Field(default_factory=list)
    requested_changes: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    max_price: Decimal | None = None

from decimal import Decimal
from typing import Literal
from pydantic import AnyHttpUrl, BaseModel, Field
class Product(BaseModel):
    title: str
    source_url: AnyHttpUrl
    category: Literal["jacket"] = "jacket"
    images: list[AnyHttpUrl] = Field(default_factory=list)
    price: Decimal | None = None
    currency: str | None = None
    attributes: dict[str, str | bool | int | float] = Field(default_factory=dict)
    extraction_status: Literal["complete", "partial", "failed"] = "partial"

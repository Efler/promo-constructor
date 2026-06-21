from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

PromotionCardTone = Literal["brand", "teal", "orange", "blue", "grape"]
PromotionCategoryScope = Literal["all", "selected"]
PromotionStatus = Literal["active", "ending_soon", "upcoming", "closed"]
PromotionParticipationStatus = Literal["active", "scheduled", "completed"]


class PromotionCatalogItem(BaseModel):
    id: int
    slug: str
    title: str
    short_description: str
    starts_on: date
    ends_on: date
    join_deadline: date
    minimum_discount_percent: int
    minimum_stock_qty: int
    minimum_products: int
    category_scope: PromotionCategoryScope
    eligible_parent_ids: list[int]
    eligible_parent_names: list[str] | None
    benefits: list[str]
    card_tone: PromotionCardTone
    is_featured: bool
    status: PromotionStatus
    join_open: bool


class PromotionParticipationCreate(BaseModel):
    additional_discount_percent: int = Field(ge=1, le=99)
    selected_product_ids: list[int] = Field(min_length=1)
    price_change_confirmed: bool

    @field_validator("selected_product_ids")
    @classmethod
    def normalize_product_ids(cls, value: list[int]) -> list[int]:
        if any(product_id < 1 for product_id in value):
            raise ValueError("Product ids must be positive.")
        return list(dict.fromkeys(value))

    @model_validator(mode="after")
    def validate_confirmation(self) -> "PromotionParticipationCreate":
        if not self.price_change_confirmed:
            raise ValueError("Promotional price changes must be confirmed.")
        return self


class PromotionParticipationRead(BaseModel):
    id: int
    promotion_id: int
    promotion_slug: str
    promotion_title: str
    selected_product_ids: list[int]
    additional_discount_percent: int
    joined_at: datetime
    status: PromotionParticipationStatus


class PromotionParticipationCreateResponse(BaseModel):
    message: str
    participation: PromotionParticipationRead

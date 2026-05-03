from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PromoType = Literal[
    "single_buyer_single_order",
    "all_buyers_once",
    "all_buyers_limited",
]
AudienceType = Literal[
    "all",
    "bought_last_half_year",
    "not_bought_last_half_year",
]
ProductScope = Literal["all", "selected"]
DiscountMode = Literal["percent", "amount"]
CodeMode = Literal["generate", "manual"]
PromocodeStatus = Literal["active", "expired"]


class PromocodeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    starts_on: date
    ends_on: date
    discount_mode: DiscountMode
    discount_value: int = Field(gt=0)
    promo_type: PromoType
    audience_type: AudienceType
    product_scope: ProductScope
    selected_product_ids: list[int] = Field(default_factory=list)
    code_mode: CodeMode
    manual_code: str | None = Field(default=None, max_length=15)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Title must not be blank.")
        return normalized

    @field_validator("manual_code", mode="before")
    @classmethod
    def normalize_manual_code(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().upper()
        return normalized or None

    @model_validator(mode="after")
    def validate_payload(self) -> "PromocodeCreate":
        if self.ends_on < self.starts_on:
            raise ValueError("End date must not be earlier than start date.")

        if (self.ends_on - self.starts_on).days + 1 > 31:
            raise ValueError("Promocode duration must not exceed 31 days.")

        if self.discount_mode == "percent" and not 1 <= self.discount_value <= 99:
            raise ValueError("Percent discount must be between 1 and 99.")

        if self.discount_mode == "amount" and self.discount_value < 1:
            raise ValueError("Fixed discount must be at least 1.")

        if self.product_scope == "all" and self.selected_product_ids:
            raise ValueError("Selected product ids are not allowed when product scope is all.")

        if self.product_scope == "selected" and not self.selected_product_ids:
            raise ValueError("At least one product must be selected.")

        if self.code_mode == "generate":
            if self.manual_code is not None:
                raise ValueError("Manual code must be empty when code mode is generate.")
        else:
            if self.manual_code is None:
                raise ValueError("Manual code is required when code mode is manual.")

            if not self.manual_code.isascii() or not self.manual_code.isalnum():
                raise ValueError("Manual code must contain only latin letters and digits.")

            if not 4 <= len(self.manual_code) <= 15:
                raise ValueError("Manual code must contain from 4 to 15 characters.")

        self.selected_product_ids = list(dict.fromkeys(self.selected_product_ids))
        return self


class PromocodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_id: int
    title: str
    starts_on: date
    ends_on: date
    discount_mode: DiscountMode
    discount_value: int
    promo_type: PromoType
    audience_type: AudienceType
    product_scope: ProductScope
    code: str
    status: PromocodeStatus
    selected_product_ids: list[int]
    created_at: datetime
    updated_at: datetime


class PromocodeCreateResponse(BaseModel):
    message: str
    promocode: PromocodeRead


class PromocodeCodeAvailability(BaseModel):
    code: str
    normalized_code: str
    is_available: bool


class PromocodeListItem(BaseModel):
    id: int
    title: str
    code: str
    starts_on: date
    ends_on: date
    discount_mode: DiscountMode
    discount_value: int
    status: PromocodeStatus
    created_at: datetime

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductItemCreate(BaseModel):
    size_id: int | None = None
    tech_size_name: str = Field(default="ONE SIZE", min_length=1, max_length=100)
    barcode: str | None = Field(default=None, max_length=64)
    price: Decimal = Field(ge=0)
    discounted_price: Decimal | None = Field(default=None, ge=0)
    club_discounted_price: Decimal | None = Field(default=None, ge=0)
    currency_code: str = Field(default="RUB", min_length=3, max_length=3)
    discount_percent: int = Field(default=0, ge=0, le=100)
    club_discount_percent: int = Field(default=0, ge=0, le=100)
    editable_size_price: bool = False
    is_bad_turnover: bool = False
    stock_qty: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    size_id: int | None
    tech_size_name: str
    barcode: str | None
    price: Decimal
    discounted_price: Decimal | None
    club_discounted_price: Decimal | None
    currency_code: str
    discount_percent: int
    club_discount_percent: int
    editable_size_price: bool
    is_bad_turnover: bool
    stock_qty: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductCreate(BaseModel):
    nm_id: int | None = None
    imt_id: int | None = None
    vendor_code: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    brand: str | None = Field(default=None, max_length=255)
    description: str | None = None
    subject_id: int | None = None
    subject_name: str | None = Field(default=None, max_length=255)
    parent_id: int | None = None
    parent_name: str | None = Field(default=None, max_length=255)
    kiz_marked: bool = False
    main_photo_url: str | None = None
    is_active: bool = True
    items: list[ProductItemCreate] = Field(min_length=1)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_id: int
    nm_id: int | None
    imt_id: int | None
    vendor_code: str
    title: str
    brand: str | None
    description: str | None
    subject_id: int | None
    subject_name: str | None
    parent_id: int | None
    parent_name: str | None
    kiz_marked: bool
    main_photo_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: list[ProductItemRead]


class ProductBundleCard(BaseModel):
    id: int
    title: str
    brand: str | None
    description: str | None
    subject_name: str | None
    parent_name: str | None
    main_photo_url: str | None
    is_active: bool
    item_count: int
    total_stock_qty: int
    min_price: Decimal
    min_discounted_price: Decimal | None
    max_discount_percent: int
    sizes: list[str]

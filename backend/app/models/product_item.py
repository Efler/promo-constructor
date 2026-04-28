from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class ProductItem(TimestampMixin, Base):
    __tablename__ = "product_items"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "tech_size_name",
            name="uq_product_items_product_size_name",
        ),
        UniqueConstraint("product_id", "size_id", name="uq_product_items_product_size_id"),
        CheckConstraint("price >= 0", name="chk_product_items_price_non_negative"),
        CheckConstraint(
            "discounted_price is null or discounted_price >= 0",
            name="chk_product_items_discounted_price_non_negative",
        ),
        CheckConstraint(
            "club_discounted_price is null or club_discounted_price >= 0",
            name="chk_product_items_club_discounted_price_non_negative",
        ),
        CheckConstraint("stock_qty >= 0", name="chk_product_items_stock_qty_non_negative"),
        CheckConstraint(
            "discount_percent between 0 and 100",
            name="chk_product_items_discount_percent_range",
        ),
        CheckConstraint(
            "club_discount_percent between 0 and 100",
            name="chk_product_items_club_discount_percent_range",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
    )
    size_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    tech_size_name: Mapped[str] = mapped_column(String(100), default="ONE SIZE")
    barcode: Mapped[str | None] = mapped_column(String(64), unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discounted_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    club_discounted_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency_code: Mapped[str] = mapped_column(String(3), default="RUB")
    discount_percent: Mapped[int] = mapped_column(SmallInteger, default=0)
    club_discount_percent: Mapped[int] = mapped_column(SmallInteger, default=0)
    editable_size_price: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_bad_turnover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stock_qty: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    product: Mapped["Product"] = relationship(back_populates="items")

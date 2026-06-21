from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    Index,
    Integer,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.promotion_benefit import PromotionBenefit
    from app.models.promotion_category import PromotionCategory
    from app.models.promotion_participation import PromotionParticipation


class Promotion(TimestampMixin, Base):
    __tablename__ = "promotions"
    __table_args__ = (
        CheckConstraint(
            "slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'",
            name="chk_promotions_slug_format",
        ),
        CheckConstraint(
            "length(btrim(title)) > 0",
            name="chk_promotions_title_not_blank",
        ),
        CheckConstraint(
            "length(btrim(short_description)) > 0",
            name="chk_promotions_description_not_blank",
        ),
        CheckConstraint("ends_on >= starts_on", name="chk_promotions_dates_order"),
        CheckConstraint(
            "join_deadline <= ends_on",
            name="chk_promotions_join_deadline",
        ),
        CheckConstraint(
            "minimum_discount_percent between 1 and 99",
            name="chk_promotions_discount_range",
        ),
        CheckConstraint(
            "minimum_stock_qty >= 0",
            name="chk_promotions_stock_non_negative",
        ),
        CheckConstraint(
            "minimum_products >= 1",
            name="chk_promotions_minimum_products_positive",
        ),
        CheckConstraint(
            "category_scope in ('all', 'selected')",
            name="chk_promotions_category_scope",
        ),
        CheckConstraint(
            "card_tone in ('brand', 'teal', 'orange', 'blue', 'grape')",
            name="chk_promotions_card_tone",
        ),
        Index(
            "ix_promotions_catalog_period",
            "starts_on",
            "ends_on",
            postgresql_where=text("is_published = true"),
        ),
        Index(
            "ix_promotions_join_deadline_published",
            "join_deadline",
            postgresql_where=text("is_published = true"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(120))
    short_description: Mapped[str] = mapped_column(String(500))
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date)
    join_deadline: Mapped[date] = mapped_column(Date)
    minimum_discount_percent: Mapped[int] = mapped_column(SmallInteger)
    minimum_stock_qty: Mapped[int] = mapped_column(Integer, default=0)
    minimum_products: Mapped[int] = mapped_column(Integer, default=1)
    category_scope: Mapped[str] = mapped_column(String(16), default="all")
    card_tone: Mapped[str] = mapped_column(String(16), default="brand")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    benefits: Mapped[list["PromotionBenefit"]] = relationship(
        back_populates="promotion",
        cascade="all, delete-orphan",
        order_by="PromotionBenefit.position",
    )
    categories: Mapped[list["PromotionCategory"]] = relationship(
        back_populates="promotion",
        cascade="all, delete-orphan",
        order_by="PromotionCategory.parent_id",
    )
    participations: Mapped[list["PromotionParticipation"]] = relationship(
        back_populates="promotion",
    )

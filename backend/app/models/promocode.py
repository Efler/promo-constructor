from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.promocode_product import PromocodeProduct
    from app.models.seller import Seller


class Promocode(TimestampMixin, Base):
    __tablename__ = "promocodes"
    __table_args__ = (
        CheckConstraint("length(btrim(title)) > 0", name="chk_promocodes_title_not_blank"),
        CheckConstraint("ends_on >= starts_on", name="chk_promocodes_dates_order"),
        CheckConstraint(
            "ends_on <= starts_on + 30",
            name="chk_promocodes_duration_max_31_days",
        ),
        CheckConstraint(
            "discount_mode in ('percent', 'amount')",
            name="chk_promocodes_discount_mode",
        ),
        CheckConstraint(
            "discount_value > 0",
            name="chk_promocodes_discount_value_positive",
        ),
        CheckConstraint(
            "("
            "(discount_mode = 'percent' and discount_value between 1 and 99)"
            " or "
            "(discount_mode = 'amount' and discount_value >= 1)"
            ")",
            name="chk_promocodes_discount_percent_range",
        ),
        CheckConstraint(
            "promo_type in ("
            "'single_buyer_single_order', "
            "'all_buyers_once', "
            "'all_buyers_limited'"
            ")",
            name="chk_promocodes_promo_type",
        ),
        CheckConstraint(
            "audience_type in ("
            "'all', "
            "'bought_last_half_year', "
            "'not_bought_last_half_year'"
            ")",
            name="chk_promocodes_audience_type",
        ),
        CheckConstraint(
            "product_scope in ('all', 'selected')",
            name="chk_promocodes_product_scope",
        ),
        CheckConstraint(
            "code ~ '^[A-Za-z0-9]{4,15}$'",
            name="chk_promocodes_code_format",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    seller_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sellers.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(50))
    starts_on: Mapped[date] = mapped_column(Date, index=True)
    ends_on: Mapped[date] = mapped_column(Date, index=True)
    discount_mode: Mapped[str] = mapped_column(String(16))
    discount_value: Mapped[int] = mapped_column(Integer)
    promo_type: Mapped[str] = mapped_column(String(40), index=True)
    audience_type: Mapped[str] = mapped_column(String(40), index=True)
    product_scope: Mapped[str] = mapped_column(String(16))
    code: Mapped[str] = mapped_column(String(15), unique=True)

    seller: Mapped["Seller"] = relationship(back_populates="promocodes")
    product_links: Mapped[list["PromocodeProduct"]] = relationship(
        back_populates="promocode",
        cascade="all, delete-orphan",
    )

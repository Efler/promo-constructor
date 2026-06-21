from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    SmallInteger,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.promotion import Promotion
    from app.models.promotion_participation_product import PromotionParticipationProduct
    from app.models.seller import Seller


class PromotionParticipation(TimestampMixin, Base):
    __tablename__ = "promotion_participations"
    __table_args__ = (
        UniqueConstraint(
            "seller_id",
            "promotion_id",
            name="uq_promotion_participations_seller_promotion",
        ),
        CheckConstraint(
            "additional_discount_percent between 1 and 99",
            name="chk_promotion_participations_discount_range",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    promotion_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("promotions.id", ondelete="RESTRICT"),
        index=True,
    )
    seller_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sellers.id", ondelete="CASCADE"),
    )
    additional_discount_percent: Mapped[int] = mapped_column(SmallInteger)
    price_change_confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    promotion: Mapped["Promotion"] = relationship(back_populates="participations")
    seller: Mapped["Seller"] = relationship(back_populates="promotion_participations")
    product_links: Mapped[list["PromotionParticipationProduct"]] = relationship(
        back_populates="participation",
        cascade="all, delete-orphan",
    )

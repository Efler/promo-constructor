from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.promotion import Promotion


class PromotionBenefit(Base):
    __tablename__ = "promotion_benefits"
    __table_args__ = (
        CheckConstraint(
            "position between 1 and 2",
            name="chk_promotion_benefits_position",
        ),
        CheckConstraint(
            "length(btrim(description)) > 0",
            name="chk_promotion_benefits_description_not_blank",
        ),
    )

    promotion_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("promotions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    promotion: Mapped["Promotion"] = relationship(back_populates="benefits")

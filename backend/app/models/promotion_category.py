from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.promotion import Promotion


class PromotionCategory(Base):
    __tablename__ = "promotion_categories"
    __table_args__ = (
        CheckConstraint(
            "parent_id > 0",
            name="chk_promotion_categories_parent_id_positive",
        ),
        CheckConstraint(
            "length(btrim(parent_name)) > 0",
            name="chk_promotion_categories_name_not_blank",
        ),
    )

    promotion_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("promotions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    parent_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    parent_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    promotion: Mapped["Promotion"] = relationship(back_populates="categories")

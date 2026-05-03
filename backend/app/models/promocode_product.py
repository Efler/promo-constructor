from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.promocode import Promocode


class PromocodeProduct(Base):
    __tablename__ = "promocode_products"

    promocode_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("promocodes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    promocode: Mapped["Promocode"] = relationship(back_populates="product_links")
    product: Mapped["Product"] = relationship(back_populates="promocode_links")

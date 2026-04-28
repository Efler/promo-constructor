from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.seller import Seller


class RefreshSession(TimestampMixin, Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    seller_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sellers.id", ondelete="CASCADE"),
        index=True,
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    seller: Mapped["Seller"] = relationship(back_populates="refresh_sessions")

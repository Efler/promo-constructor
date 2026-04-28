from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SellerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    email: str | None
    seller_sid: UUID | None
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

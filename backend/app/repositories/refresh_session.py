from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.refresh_session import RefreshSession


def get_refresh_session_by_id(db: Session, session_id: UUID) -> RefreshSession | None:
    return db.get(RefreshSession, session_id)


def add_refresh_session(db: Session, refresh_session: RefreshSession) -> RefreshSession:
    db.add(refresh_session)
    return refresh_session


def revoke_refresh_session(
    refresh_session: RefreshSession,
    *,
    revoked_at: datetime,
) -> RefreshSession:
    refresh_session.revoked_at = revoked_at
    return refresh_session

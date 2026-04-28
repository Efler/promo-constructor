from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_secret,
    verify_password,
    verify_secret,
)
from app.models.refresh_session import RefreshSession
from app.models.seller import Seller
from app.repositories.refresh_session import (
    add_refresh_session,
    get_refresh_session_by_id,
    revoke_refresh_session,
)
from app.repositories.seller import add_seller, get_seller_by_email, get_seller_by_username
from app.schemas.auth import LoginRequest, RegisterRequest


@dataclass
class AuthPayload:
    seller: Seller
    access_token: str
    refresh_token: str


def _normalize_display_name(username: str, display_name: str | None) -> str:
    if display_name and display_name.strip():
        return display_name.strip()
    return username.strip().replace("_", " ").title()


def _refresh_expiration() -> datetime:
    return datetime.now(UTC) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)


def _build_auth_payload(db: Session, seller: Seller) -> AuthPayload:
    now = datetime.now(UTC)
    session_id = uuid4()
    refresh_token = create_refresh_token(seller=seller, session_id=session_id)
    refresh_session = RefreshSession(
        id=session_id,
        seller_id=seller.id,
        refresh_token_hash=hash_secret(refresh_token),
        expires_at=_refresh_expiration(),
        last_used_at=now,
    )
    add_refresh_session(db, refresh_session)
    access_token = create_access_token(seller=seller)

    return AuthPayload(
        seller=seller,
        access_token=access_token,
        refresh_token=refresh_token,
    )


def register_seller(db: Session, payload: RegisterRequest) -> AuthPayload:
    username = payload.username.strip()
    if get_seller_by_username(db, username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seller with this username already exists.",
        )

    if payload.email and get_seller_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seller with this email already exists.",
        )

    seller = Seller(
        username=username,
        password_hash=hash_password(payload.password),
        display_name=_normalize_display_name(username, payload.display_name),
        email=payload.email,
        is_active=True,
        last_login_at=datetime.now(UTC),
    )
    add_seller(db, seller)
    db.flush()

    auth_payload = _build_auth_payload(db, seller)
    db.commit()
    db.refresh(seller)
    return auth_payload


def login_seller(db: Session, payload: LoginRequest) -> AuthPayload:
    seller = get_seller_by_username(db, payload.username.strip())
    if seller is None or not verify_password(payload.password, seller.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if not seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller account is inactive.",
        )

    seller.last_login_at = datetime.now(UTC)
    auth_payload = _build_auth_payload(db, seller)
    db.commit()
    db.refresh(seller)
    return auth_payload


def refresh_seller_session(db: Session, refresh_token: str) -> AuthPayload:
    payload = decode_token(refresh_token, expected_type="refresh")

    try:
        seller_id = int(payload["sub"])
        session_id = UUID(str(payload["session_id"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh session.",
        ) from exc

    refresh_session = get_refresh_session_by_id(db, session_id)
    if refresh_session is None or refresh_session.seller_id != seller_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session not found.",
        )

    now = datetime.now(UTC)
    if refresh_session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session has been revoked.",
        )

    if refresh_session.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session has expired.",
        )

    if not verify_secret(refresh_token, refresh_session.refresh_token_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session is invalid.",
        )

    seller = refresh_session.seller
    if seller is None or not seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seller account is unavailable.",
        )

    new_refresh_token = create_refresh_token(seller=seller, session_id=refresh_session.id)
    refresh_session.refresh_token_hash = hash_secret(new_refresh_token)
    refresh_session.expires_at = _refresh_expiration()
    refresh_session.last_used_at = now

    db.commit()
    db.refresh(seller)

    return AuthPayload(
        seller=seller,
        access_token=create_access_token(seller=seller),
        refresh_token=new_refresh_token,
    )


def logout_seller_session(db: Session, refresh_token: str | None) -> None:
    if not refresh_token:
        return

    try:
        payload = decode_token(refresh_token, expected_type="refresh")
        session_id = UUID(str(payload["session_id"]))
    except Exception:
        return

    refresh_session = get_refresh_session_by_id(db, session_id)
    if refresh_session is None or refresh_session.revoked_at is not None:
        return

    revoke_refresh_session(refresh_session, revoked_at=datetime.now(UTC))
    db.commit()

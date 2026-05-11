from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash

from app.core.config import settings
from app.models.seller import Seller

password_hash = PasswordHash.recommended()


def hash_secret(secret: str) -> str:
    return password_hash.hash(secret)


def verify_secret(secret: str, secret_hash: str) -> bool:
    return password_hash.verify(secret, secret_hash)


def hash_password(password: str) -> str:
    return hash_secret(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return verify_secret(password, hashed_password)


def verify_api_admin_key(candidate: str | None) -> bool:
    if not candidate or not settings.API_ADMIN_KEY:
        return False

    return hmac.compare_digest(candidate, settings.API_ADMIN_KEY)


def build_api_admin_cookie_value() -> str:
    return hashlib.sha256(settings.API_ADMIN_KEY.encode("utf-8")).hexdigest()


def verify_api_admin_cookie_value(candidate: str | None) -> bool:
    if not candidate or not settings.API_ADMIN_KEY:
        return False

    expected = build_api_admin_cookie_value()
    return hmac.compare_digest(candidate, expected)


def _create_token(
    *,
    seller: Seller,
    token_type: str,
    expires_minutes: int,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {
        "sub": str(seller.id),
        "username": seller.username,
        "display_name": seller.display_name,
        "type": token_type,
        "exp": expires_at,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(*, seller: Seller) -> str:
    return _create_token(
        seller=seller,
        token_type="access",
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_refresh_token(*, seller: Seller, session_id: UUID) -> str:
    return _create_token(
        seller=seller,
        token_type="refresh",
        expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        extra_claims={"session_id": str(session_id)},
    )


def decode_token(token: str, *, expected_type: str) -> dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token.",
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError as exc:
        raise credentials_exception from exc

    if payload.get("type") != expected_type:
        raise credentials_exception

    return payload

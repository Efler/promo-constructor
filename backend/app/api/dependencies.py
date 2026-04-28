from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.seller import Seller
from app.repositories.seller import get_seller_by_id


def get_current_seller(
    request: Request,
    db: Session = Depends(get_db),
) -> Seller:
    token = request.cookies.get(settings.ACCESS_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    payload = decode_token(token, expected_type="access")
    subject = payload.get("sub")

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seller context is missing.",
        )

    try:
        seller_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seller context is invalid.",
        ) from exc

    seller = get_seller_by_id(db, seller_id)
    if seller is None or not seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seller account is unavailable.",
        )

    return seller

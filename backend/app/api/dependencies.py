from fastapi import HTTPException, Request, status

from app.core.config import settings
from app.core.security import decode_token
from app.schemas.auth import SellerIdentity


def get_current_seller(request: Request) -> SellerIdentity:
    token = request.cookies.get(settings.ACCESS_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    payload = decode_token(token, expected_type="access")
    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seller context is missing.",
        )

    display_name = payload.get("display_name") or username
    return SellerIdentity(username=username, display_name=display_name)

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.config import settings
from app.core.security import create_token, decode_token
from app.schemas.auth import AuthResponse, LoginRequest, SellerIdentity

router = APIRouter(prefix="/auth", tags=["auth"])


def _normalize_seller(username: str) -> SellerIdentity:
    normalized = username.strip() or "seller"
    display_name = normalized.replace("_", " ").title()
    return SellerIdentity(username=normalized, display_name=display_name)


def _set_auth_cookies(response: Response, seller: SellerIdentity) -> None:
    access_token = create_token(
        subject=seller.username,
        display_name=seller.display_name,
        token_type="access",
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = create_token(
        subject=seller.username,
        display_name=seller.display_name,
        token_type="refresh",
        expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    cookie_common = {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "path": "/",
    }

    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **cookie_common,
    )
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        **cookie_common,
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response) -> AuthResponse:
    seller = _normalize_seller(payload.username)
    _set_auth_cookies(response, seller)
    return AuthResponse(message="Seller session initialized.", seller=seller)


@router.post("/refresh", response_model=AuthResponse)
def refresh(request: Request, response: Response) -> AuthResponse:
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing.",
        )

    payload = decode_token(refresh_token, expected_type="refresh")
    seller = _normalize_seller(str(payload.get("sub", "")))
    _set_auth_cookies(response, seller)

    return AuthResponse(message="Seller session refreshed.", seller=seller)


@router.get("/me", response_model=AuthResponse)
def me(request: Request) -> AuthResponse:
    access_token = request.cookies.get(settings.ACCESS_COOKIE_NAME)

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    payload = decode_token(access_token, expected_type="access")
    seller = _normalize_seller(str(payload.get("sub", "")))
    return AuthResponse(message="Seller session is active.", seller=seller)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie(settings.ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")
    return response

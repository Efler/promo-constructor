from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_seller
from app.core.config import settings
from app.db.session import get_db
from app.models.seller import Seller
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.seller import SellerRead
from app.services.auth import login_seller, logout_seller_session, refresh_seller_session, register_seller

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(
    response: Response,
    *,
    access_token: str,
    refresh_token: str,
) -> None:
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


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    auth_payload = register_seller(db, payload)
    _set_auth_cookies(
        response,
        access_token=auth_payload.access_token,
        refresh_token=auth_payload.refresh_token,
    )
    return AuthResponse(
        message="Seller account created.",
        seller=SellerRead.model_validate(auth_payload.seller),
    )


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    auth_payload = login_seller(db, payload)
    _set_auth_cookies(
        response,
        access_token=auth_payload.access_token,
        refresh_token=auth_payload.refresh_token,
    )
    return AuthResponse(
        message="Seller session initialized.",
        seller=SellerRead.model_validate(auth_payload.seller),
    )


@router.post("/refresh", response_model=AuthResponse)
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing.",
        )

    auth_payload = refresh_seller_session(db, refresh_token)
    _set_auth_cookies(
        response,
        access_token=auth_payload.access_token,
        refresh_token=auth_payload.refresh_token,
    )
    return AuthResponse(
        message="Seller session refreshed.",
        seller=SellerRead.model_validate(auth_payload.seller),
    )


@router.get("/me", response_model=AuthResponse)
def me(current_seller: Seller = Depends(get_current_seller)) -> AuthResponse:
    return AuthResponse(
        message="Seller session is active.",
        seller=SellerRead.model_validate(current_seller),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> Response:
    logout_seller_session(db, request.cookies.get(settings.REFRESH_COOKIE_NAME))
    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie(settings.ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")
    return response

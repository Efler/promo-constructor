from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.seller import SellerRead


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=255)
    display_name: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)


class AuthResponse(BaseModel):
    message: str
    seller: SellerRead

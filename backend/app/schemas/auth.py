from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)


class SellerIdentity(BaseModel):
    username: str
    display_name: str


class AuthResponse(BaseModel):
    message: str
    seller: SellerIdentity

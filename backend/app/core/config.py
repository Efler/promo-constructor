from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Promo Constructor API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "dev"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = (
        "postgresql+psycopg://admin:admin@localhost:5432/promo_constructor"
    )
    SECRET_KEY: str = "123456789"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 180
    ACCESS_COOKIE_NAME: str = "pc_access_token"
    REFRESH_COOKIE_NAME: str = "pc_refresh_token"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    API_ADMIN_PROTECTION_ENABLED: bool = True
    API_ADMIN_KEY: str = "123-456-789"
    API_ADMIN_COOKIE_NAME: str = "pc_api_admin_access"
    API_ADMIN_COOKIE_MAX_AGE_MINUTES: int = 720
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ]
    )

    @model_validator(mode="after")
    def validate_api_admin_protection(self) -> "Settings":
        if self.API_ADMIN_PROTECTION_ENABLED and not self.API_ADMIN_KEY:
            raise ValueError(
                "API_ADMIN_KEY must be configured when API_ADMIN_PROTECTION_ENABLED is true."
            )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()

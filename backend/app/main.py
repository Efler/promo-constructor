from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.security import verify_api_admin_cookie_value, verify_api_admin_key
from app.modules.api_access.router import router as api_access_router


def _is_protected_path(path: str) -> bool:
    protected_docs = {"/docs", "/redoc", "/swagger"}
    return path.startswith(settings.API_V1_PREFIX) or path in protected_docs


def _api_admin_required_response() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "detail": "Backend API admin key required.",
            "code": "api_admin_key_required",
        },
    )


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def api_admin_protection(request: Request, call_next):
        if not settings.API_ADMIN_PROTECTION_ENABLED or not _is_protected_path(request.url.path):
            return await call_next(request)

        header_key = request.headers.get("X-Admin-Key")
        if verify_api_admin_key(header_key):
            return await call_next(request)

        cookie_value = request.cookies.get(settings.API_ADMIN_COOKIE_NAME)
        if verify_api_admin_cookie_value(cookie_value):
            return await call_next(request)

        return _api_admin_required_response()

    @app.get("/", tags=["system"])
    def read_root() -> dict[str, str]:
        return {
            "project": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
            "api": settings.API_V1_PREFIX,
        }

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/swagger", tags=["system"], include_in_schema=False)
    def swagger_ui():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url or f"{settings.API_V1_PREFIX}/openapi.json",
            title=f"{settings.PROJECT_NAME} - Swagger UI",
        )

    app.include_router(api_access_router)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()

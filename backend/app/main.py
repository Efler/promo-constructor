from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.security import verify_api_admin_key, verify_frontend_internal_api_key


def _is_api_path(path: str) -> bool:
    return path.startswith(settings.API_V1_PREFIX)


def _is_docs_path(path: str) -> bool:
    return path in {"/docs", "/redoc", "/swagger"}


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
        if not settings.API_ADMIN_PROTECTION_ENABLED:
            return await call_next(request)

        path = request.url.path

        if _is_api_path(path):
            header_key = request.headers.get("X-Admin-Key")
            frontend_proxy_key = request.headers.get("X-Frontend-Proxy-Key")
            if verify_api_admin_key(header_key) or verify_frontend_internal_api_key(
                frontend_proxy_key
            ):
                return await call_next(request)

            return _api_admin_required_response()

        if _is_docs_path(path):
            header_key = request.headers.get("X-Admin-Key")
            if verify_api_admin_key(header_key):
                return await call_next(request)

            return _api_admin_required_response()

        return await call_next(request)

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

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()

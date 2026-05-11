from __future__ import annotations

from html import escape

from fastapi import APIRouter, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.config import settings
from app.core.security import build_api_admin_cookie_value, verify_api_admin_cookie_value, verify_api_admin_key

router = APIRouter(tags=["api-access"])


def _normalize_next_path(next_path: str | None) -> str:
    if not next_path or not next_path.startswith("/") or next_path.startswith("//"):
        return "/"
    return next_path


def _build_page(*, next_path: str, error_message: str | None = None) -> str:
    error_block = ""
    if error_message:
        error_block = (
            '<p style="color:#b42318;background:#fef3f2;border:1px solid #fecdca;'
            'padding:12px 14px;border-radius:10px;margin:0 0 16px;">'
            f"{escape(error_message)}</p>"
        )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Backend API Access</title>
    <style>
      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: linear-gradient(145deg, #f4efe7 0%, #e7edf5 100%);
        font-family: Arial, sans-serif;
        color: #182230;
      }}
      .card {{
        width: min(420px, calc(100vw - 32px));
        background: rgba(255,255,255,0.96);
        border: 1px solid #d5d9e3;
        border-radius: 18px;
        box-shadow: 0 24px 60px rgba(24, 34, 48, 0.12);
        padding: 28px;
      }}
      h1 {{
        margin: 0 0 10px;
        font-size: 28px;
      }}
      p {{
        margin: 0 0 16px;
        line-height: 1.5;
      }}
      label {{
        display: block;
        margin-bottom: 8px;
        font-size: 14px;
        font-weight: 700;
      }}
      input {{
        width: 100%;
        box-sizing: border-box;
        padding: 12px 14px;
        border: 1px solid #c5cad5;
        border-radius: 12px;
        font-size: 15px;
        margin-bottom: 16px;
      }}
      button {{
        width: 100%;
        border: 0;
        border-radius: 12px;
        padding: 12px 16px;
        background: #182230;
        color: #fff;
        font-size: 15px;
        font-weight: 700;
        cursor: pointer;
      }}
      code {{
        font-family: Consolas, monospace;
      }}
    </style>
  </head>
  <body>
    <main class="card">
      <h1>Backend API Access</h1>
      <p>Enter the pre-configured admin key to unlock API and Swagger access for this browser.</p>
      {error_block}
      <form method="post" action="/api-access">
        <input type="hidden" name="next" value="{escape(next_path)}" />
        <label for="admin_key">Admin key</label>
        <input id="admin_key" name="admin_key" type="password" autocomplete="current-password" required />
        <button type="submit">Unlock access</button>
      </form>
      <p style="margin-top:16px;font-size:13px;color:#475467;">
        Script clients can also send <code>X-Admin-Key</code> with each request.
      </p>
    </main>
  </body>
</html>"""


def _set_api_admin_cookie(response: Response) -> None:
    response.set_cookie(
        key=settings.API_ADMIN_COOKIE_NAME,
        value=build_api_admin_cookie_value(),
        max_age=settings.API_ADMIN_COOKIE_MAX_AGE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )


@router.get("/api-access", include_in_schema=False)
def api_access_page(request: Request, next: str = "/") -> Response:
    next_path = _normalize_next_path(next)

    if not settings.API_ADMIN_PROTECTION_ENABLED:
        return RedirectResponse(url=next_path, status_code=status.HTTP_303_SEE_OTHER)

    existing_cookie = request.cookies.get(settings.API_ADMIN_COOKIE_NAME)
    if verify_api_admin_cookie_value(existing_cookie):
        return RedirectResponse(url=next_path, status_code=status.HTTP_303_SEE_OTHER)

    return HTMLResponse(_build_page(next_path=next_path))


@router.post("/api-access", include_in_schema=False)
def api_access_unlock(
    admin_key: str = Form(...),
    next: str = Form("/"),
) -> Response:
    next_path = _normalize_next_path(next)

    if not settings.API_ADMIN_PROTECTION_ENABLED:
        return RedirectResponse(url=next_path, status_code=status.HTTP_303_SEE_OTHER)

    if not verify_api_admin_key(admin_key):
        return HTMLResponse(
            _build_page(next_path=next_path, error_message="Invalid admin key."),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    response = RedirectResponse(url=next_path, status_code=status.HTTP_303_SEE_OTHER)
    _set_api_admin_cookie(response)
    return response


@router.post("/api-access/logout", include_in_schema=False)
def api_access_logout() -> Response:
    response = RedirectResponse(url="/api-access", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(settings.API_ADMIN_COOKIE_NAME, path="/")
    return response

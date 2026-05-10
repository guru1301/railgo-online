import os
import secrets
from typing import Optional

from fastapi import Header, HTTPException, Request, Response

from app.auth import decode_token


SESSION_COOKIE_NAME = "railgo_session"
CSRF_COOKIE_NAME = "railgo_csrf"
SESSION_COOKIE_MAX_AGE = int(os.getenv("SESSION_COOKIE_MAX_AGE", str(60 * 60 * 24 * 7)))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


def set_csrf_cookie(response: Response) -> str:
    csrf_token = secrets.token_urlsafe(32)
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=False,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )
    return csrf_token


def get_token_from_request(request: Request) -> Optional[str]:
    authorization = request.headers.get("authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1]
    return request.cookies.get(SESSION_COOKIE_NAME)


def get_current_user_id(request: Request) -> int:
    token = get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(payload["sub"])


def verify_csrf(
    request: Request,
    x_csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token"),
) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    if not cookie_token or not x_csrf_token or cookie_token != x_csrf_token:
        raise HTTPException(status_code=403, detail="CSRF validation failed")

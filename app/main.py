import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import engine, Base
from app.rate_limit import limiter
from app.routers import trains, bookings, pnr, tracking, auth, passengers
from app.security import CSRF_COOKIE_NAME

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RailGo API (Python/PostgreSQL)")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Too many requests, slow down."})


@app.on_event("startup")
async def startup_cache():
    FastAPICache.init(InMemoryBackend(), prefix="railgo-cache")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = "default-src 'self' https: data: blob: 'unsafe-inline'"
        return response


# CORS
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8001,http://127.0.0.1:8001,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)


@app.middleware("http")
async def csrf_middleware(request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.url.path.startswith("/api/"):
        # Only enforce CSRF when session cookie is present.
        if request.cookies.get("railgo_session"):
            cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
            header_token = request.headers.get("X-CSRF-Token")
            if not cookie_token or not header_token or cookie_token != header_token:
                return JSONResponse(status_code=403, content={"detail": "CSRF validation failed"})
    return await call_next(request)

# API Routers
app.include_router(trains.router)
app.include_router(bookings.router)
app.include_router(pnr.router)
app.include_router(tracking.router)
app.include_router(auth.router)
app.include_router(passengers.router)

# Mount static files for frontend (Fallback for local dev)
try:
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.exists(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
except RuntimeError:
    pass # Vercel handles static routing directly via vercel.json

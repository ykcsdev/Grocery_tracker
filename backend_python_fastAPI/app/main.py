import threading
import os
from fastapi import FastAPI
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.routers import receipts, invoices, dashboard, chat
from app.limiter import limiter
from app.services.scheduler import receipt_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grocery Receipt API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def _csv_env(name: str) -> list[str]:
    return [
        value.strip()
        for value in os.getenv(name, "").split(",")
        if value.strip()
    ]


def _build_origin(scheme: str, host: str, port: str) -> str | None:
    if not host:
        return None

    normalized_scheme = scheme or "http"
    normalized_port = port.strip()
    default_port = "443" if normalized_scheme == "https" else "80"

    if not normalized_port or normalized_port == default_port:
        return f"{normalized_scheme}://{host}"

    return f"{normalized_scheme}://{host}:{normalized_port}"


configured_origins = _csv_env("CORS_ALLOWED_ORIGINS")
derived_origin = _build_origin(
    os.getenv("APP_SCHEME", "http").strip(),
    os.getenv("DEPLOY_DOMAIN", "").strip(),
    os.getenv("FRONTEND_PORT_EXTERNAL", "").strip(),
)
allow_origins = configured_origins or ([derived_origin] if derived_origin else [])
allow_origin_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX", "").strip() or None

if not allow_origins and not allow_origin_regex:
    raise ValueError(
        "CORS configuration is missing. Set CORS_ALLOWED_ORIGINS or define "
        "APP_SCHEME, DEPLOY_DOMAIN, and FRONTEND_PORT_EXTERNAL."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(receipts.router)
app.include_router(invoices.router)
app.include_router(dashboard.router)
app.include_router(chat.router)


@app.on_event("startup")
def start_scheduler():
     thread = threading.Thread(target=receipt_scheduler, daemon=True)
     thread.start()

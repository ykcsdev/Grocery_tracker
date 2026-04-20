import threading
import os
from fastapi import FastAPI
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.routers import receipts, invoices, dashboard, chat
from app.services.scheduler import receipt_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grocery Receipt API")

default_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://localhost:80",
]
configured_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
allow_origins = configured_origins or default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
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

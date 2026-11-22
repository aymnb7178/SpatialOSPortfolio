from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .routers import admin, analytics, auth, messages, orders, payments

settings = get_settings()
app = FastAPI(title="SpatialOS Portfolio API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])
app.include_router(auth.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.app_env}

root = Path(__file__).resolve().parents[2]
public_dir = root / "public"
app.mount("/", StaticFiles(directory=public_dir, html=True), name="frontend")

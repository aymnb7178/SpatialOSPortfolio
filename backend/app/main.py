from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .routers import admin, analytics, auth, messages, orders, payments

settings = get_settings()
app = FastAPI(title="SpatialOS Portfolio API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")
MAX_API_BODY_BYTES = 1_048_576
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > MAX_API_BODY_BYTES:
            return JSONResponse({"detail": "حجم الطلب أكبر من الحد المسموح"}, status_code=413)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if origin and origin not in settings.cors_origin_list:
                return JSONResponse({"detail": "Origin غير مسموح"}, status_code=403)
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if settings.app_env.lower() == "production":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response
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

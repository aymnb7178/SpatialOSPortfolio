from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .routers import admin, analytics, auth, career, github, messages, orders, payments, projects

settings = get_settings()
app = FastAPI(title="SpatialOS Portfolio API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")
MAX_API_BODY_BYTES = 1_048_576
STATIC_CACHE_SUFFIXES = {
    ".avif", ".css", ".gif", ".ico", ".jpeg", ".jpg", ".js", ".png",
    ".svg", ".webp", ".woff", ".woff2"
}
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
    if request.method == "GET" and not request.url.path.startswith("/api/") and Path(request.url.path).suffix.lower() in STATIC_CACHE_SUFFIXES:
        response.headers.setdefault("Cache-Control", "public, max-age=604800, stale-while-revalidate=86400")
    return response
app.include_router(auth.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(projects.admin_router, prefix="/api")
app.include_router(github.router, prefix="/api")
app.include_router(github.admin_router, prefix="/api")
app.include_router(career.router, prefix="/api")
app.include_router(career.admin_router, prefix="/api")
app.include_router(career.skills_router, prefix="/api")
app.include_router(career.admin_skills_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.app_env}

root = Path(__file__).resolve().parents[2]
public_dir = root / "public"

@app.get("/project/{slug}", include_in_schema=False)
def project_page(slug: str):
    if not slug or len(slug) > 80:
        return FileResponse(public_dir / "index.html")
    return FileResponse(public_dir / "index.html")

app.mount("/", StaticFiles(directory=public_dir, html=True), name="frontend")

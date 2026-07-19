"""
AIgnition Backend — FastAPI Application Entry-point

Architecture:
  app/main.py         ← this file (app factory)
  app/routes/         ← one router per domain
  app/services/       ← business logic
  app/models/         ← Pydantic request/response shapes
  app/utils/          ← shared helpers
  app/ml_interface.py ← ML/LLM stubs (only file ML team modifies)
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.exceptions import (
    InvalidCSV,
    MLNotImplemented,
    ReportGenerationError,
    UploadNotFound,
    UnsupportedFileType,
)
from app.utils.file_utils import ensure_uploads_dir
from app.utils.logger import get_logger

from app.routes import upload, validate, forecast, optimizer, risks, summary, report, dashboard

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Lifespan (startup / shutdown)
# ──────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AIgnition API starting — version %s", settings.APP_VERSION)
    ensure_uploads_dir()
    logger.info("📁 Uploads directory ready")
    yield
    logger.info("🛑 AIgnition API shutting down")


# ──────────────────────────────────────────────────────────────────────────────
# App factory
# ──────────────────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "**AIgnition** — AI Marketing Decision Copilot API\n\n"
            "Upload marketing CSVs from Google Ads, Meta Ads, Microsoft Ads, GA4, or Shopify. "
            "Get probabilistic forecasts, budget optimisation, risk detection, and AI-generated summaries.\n\n"
            "**ML Integration**: All forecasting goes through `ml_interface.py`. "
            "The ML team only needs to implement `predict()` and `generate_summary()` — "
            "no other file changes required."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request timing middleware ─────────────────────────────────────────
    @app.middleware("http")
    async def add_process_time(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = round((time.perf_counter() - start) * 1000, 1)
        response.headers["X-Process-Time-Ms"] = str(elapsed)
        logger.info("%s %s → %d (%.1fms)", request.method, request.url.path, response.status_code, elapsed)
        return response

    # ── Exception handlers ────────────────────────────────────────────────
    @app.exception_handler(UploadNotFound)
    async def upload_not_found_handler(request: Request, exc: UploadNotFound):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(InvalidCSV)
    async def invalid_csv_handler(request: Request, exc: InvalidCSV):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(UnsupportedFileType)
    async def unsupported_file_handler(request: Request, exc: UnsupportedFileType):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(MLNotImplemented)
    async def ml_not_implemented_handler(request: Request, exc: MLNotImplemented):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(ReportGenerationError)
    async def report_error_handler(request: Request, exc: ReportGenerationError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. Check server logs."},
        )

    # ── Routers ───────────────────────────────────────────────────────────
    prefix = "/api/v1"
    app.include_router(upload.router,    prefix=prefix)
    app.include_router(validate.router,  prefix=prefix)
    app.include_router(forecast.router,  prefix=prefix)
    app.include_router(optimizer.router, prefix=prefix)
    app.include_router(risks.router,     prefix=prefix)
    app.include_router(summary.router,   prefix=prefix)
    app.include_router(report.router,    prefix=prefix)
    app.include_router(dashboard.router, prefix=prefix)

    # ── Health check ──────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health check")
    async def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()

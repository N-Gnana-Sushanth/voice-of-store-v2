"""Voice of Store Backend - FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.health import router as health_router
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.exceptions import AppException
from app.core.logging import logger, setup_logging
from app.core.middleware import CorrelationIdMiddleware, SecurityAndLimitMiddleware
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.services.classifier import classifier_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle management."""
    # 1. Initialize logging
    setup_logging(debug=settings.DEBUG)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")

    # 2. Ensure database tables exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified.")
    except Exception as e:
        logger.error(f"Database schema initialization warning: {e}", exc_info=True)

    # 3. Warm up ML classifier
    if classifier_service.is_ready():
        logger.info(f"ML Classifier loaded: {classifier_service.model_version}")
    else:
        logger.warning("ML Classifier failed to load during startup.")

    # 4. Optional initial superadmin bootstrap
    if settings.INITIAL_ADMIN_EMAIL and settings.INITIAL_ADMIN_PASSWORD:
        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.email == settings.INITIAL_ADMIN_EMAIL).first()
            if not admin_user:
                logger.info(f"Bootstrapping initial superadmin account: {settings.INITIAL_ADMIN_EMAIL}")
                superadmin = User(
                    email=settings.INITIAL_ADMIN_EMAIL,
                    hashed_password=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                    full_name="System Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
                db.add(superadmin)
                db.commit()
                logger.info("Initial superadmin created successfully.")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to bootstrap initial admin: {e}")
        finally:
            db.close()

    yield

    # Shutdown
    logger.info("Shutting down Voice of Store backend service.")


# OpenAPI documentation metadata
tags_metadata = [
    {"name": "Health", "description": "Liveness and dependency readiness probes."},
    {"name": "Authentication", "description": "User login, JWT issuance, and account provisioning."},
    {"name": "Stores", "description": "Retail store directory and exposure metadata."},
    {"name": "Feedback", "description": "Customer feedback and employee report ingestion."},
    {"name": "Incidents", "description": "Consolidated issue management, status updates, and trace links."},
    {"name": "Analytics", "description": "Incident analytics and transaction-normalized store comparisons."},
    {"name": "Emerging Issues", "description": "Statistical emerging-issue detection, baselines, and alerts."},
    {"name": "Replay & Evaluation", "description": "Chronological simulation and evaluation of planted incidents."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Intelligent feedback and emerging-issue detection platform for multi-store retail operations. "
        "Transforms customer and employee feedback into structured incidents, enforces deterministic "
        "safety and allergen escalation policies, tracks store-level trends, and detects emerging operational issues."
    ),
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. Custom Middlewares
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(SecurityAndLimitMiddleware)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Process-Time"],
)


# 3. Structured Global Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application domain exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic schema validation errors with clean structured payloads."""
    errors = []
    for err in exc.errors():
        field_loc = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": field_loc,
            "message": err.get("msg", "Validation error"),
            "type": err.get("type", "value_error"),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed. Inspect error details for invalid fields.",
                "details": {"validation_errors": errors},
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Format FastAPI HTTPExceptions into standardized JSON."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "details": {},
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler ensuring internal failures do not expose stack traces or DB credentials."""
    logger.critical(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred. Please contact system support.",
                "details": {},
            }
        },
    )


# 4. Mount Top-Level Health Probes (for Render / load balancer root path probing)
app.include_router(health_router)

# 5. Mount API Version 1 Master Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

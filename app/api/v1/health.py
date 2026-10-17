"""Health check and dependency readiness API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.schemas.common import HealthStatus, ReadinessStatus
from app.services.classifier import classifier_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthStatus, summary="Liveness Probe")
def health_check() -> HealthStatus:
    """Basic liveness probe confirming API server is running."""
    return HealthStatus(
        status="ok",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )


@router.get("/ready", response_model=ReadinessStatus, summary="Readiness Probe")
def readiness_check(db: Session = Depends(get_db)) -> ReadinessStatus:
    """
    Readiness probe validating database connectivity and ML classifier readiness.
    Distinguishes liveness from downstream dependency health.
    """
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    model_ready = classifier_service.is_ready()
    overall_status = "ready" if (db_status == "ok" and model_ready) else "degraded"

    return ReadinessStatus(
        status=overall_status,
        database=db_status,
        model_loaded=model_ready,
        version=settings.VERSION,
    )

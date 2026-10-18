"""Emerging issue alert management and evidence retrieval API endpoints."""

from datetime import datetime, timezone
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import check_store_access, get_current_user, get_db, require_roles
from app.core.exceptions import EntityNotFoundError, InvalidInputError
from app.models.alert import Alert, AlertStatus
from app.models.audit import AuditAction
from app.models.user import User, UserRole
from app.schemas.alert import (
    AlertAcknowledgeRequest,
    AlertDetailResponse,
    AlertResolveRequest,
    AlertResponse,
)
from app.schemas.common import PaginatedResponse
from app.services.audit_service import audit_service
from app.services.emerging_detector import emerging_detector

router = APIRouter(prefix="/alerts", tags=["Emerging Issues"])


@router.get(
    "",
    response_model=PaginatedResponse[AlertResponse],
    summary="List Emerging Issue Alerts",
)
def list_alerts(
    store_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AlertResponse]:
    """Retrieve emerging issue alerts with filtering and store access controls."""
    query = db.query(Alert)

    # Store manager access restriction
    if current_user.role == UserRole.STORE_MANAGER:
        if not current_user.store_id:
            query = query.filter(Alert.store_id == "NONE")
        else:
            query = query.filter(Alert.store_id == current_user.store_id)
    elif store_id:
        query = query.filter(Alert.store_id == store_id)

    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    if category:
        query = query.filter(Alert.category == category)

    total = query.count()
    items = (
        query.order_by(Alert.last_detected_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedResponse(
        items=[AlertResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/{alert_id}",
    response_model=AlertDetailResponse,
    summary="Get Alert Details with Complete Explainable Evidence",
)
def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AlertDetailResponse:
    """Retrieve full statistical evidence, Z-score, rate ratios, and peer comparisons behind an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise EntityNotFoundError("Alert", alert_id)

    check_store_access(current_user, alert.store_id)
    return AlertDetailResponse.model_validate(alert)


@router.post(
    "/scan",
    response_model=List[AlertResponse],
    summary="Trigger Emerging Issue Scan (Admin/Analyst)",
)
def trigger_scan(
    store_id: Optional[str] = Query(default=None),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST])),
    db: Session = Depends(get_db),
) -> List[AlertResponse]:
    """Manually trigger emerging issue detection scan across stores and categories."""
    alerts = emerging_detector.scan_for_emerging_issues(db=db, store_id=store_id)
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post(
    "/{alert_id}/acknowledge",
    response_model=AlertResponse,
    summary="Acknowledge Alert",
)
def acknowledge_alert(
    alert_id: str,
    body: Optional[AlertAcknowledgeRequest] = None,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STORE_MANAGER, UserRole.ANALYST])),
    db: Session = Depends(get_db),
) -> AlertResponse:
    """Acknowledge an active emerging issue alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise EntityNotFoundError("Alert", alert_id)

    check_store_access(current_user, alert.store_id)

    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by_id = current_user.id
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)

    audit_service.log_event(
        db=db,
        action=AuditAction.ALERT_ACKNOWLEDGED,
        resource_type="Alert",
        resource_id=alert.id,
        actor=current_user,
        details={"notes": body.notes if body else None},
    )

    return AlertResponse.model_validate(alert)


@router.post(
    "/{alert_id}/resolve",
    response_model=AlertResponse,
    summary="Resolve Alert",
)
def resolve_alert(
    alert_id: str,
    resolve_data: AlertResolveRequest,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STORE_MANAGER, UserRole.ANALYST])),
    db: Session = Depends(get_db),
) -> AlertResponse:
    """Resolve an alert with mandatory documented action notes."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise EntityNotFoundError("Alert", alert_id)

    check_store_access(current_user, alert.store_id)

    alert.status = AlertStatus.RESOLVED
    alert.resolved_by_id = current_user.id
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolution_notes = resolve_data.resolution_notes
    db.commit()
    db.refresh(alert)

    audit_service.log_event(
        db=db,
        action=AuditAction.ALERT_RESOLVED,
        resource_type="Alert",
        resource_id=alert.id,
        actor=current_user,
        details={"notes": resolve_data.resolution_notes},
    )

    return AlertResponse.model_validate(alert)

"""Incident management and source feedback retrieval API endpoints."""

import math
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import check_store_access, get_current_user, get_db, require_roles
from app.core.exceptions import EntityNotFoundError, InvalidInputError
from app.models.audit import AuditAction
from app.models.feedback import FeedbackRecord
from app.models.incident import Incident, IncidentStatus
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse
from app.schemas.feedback import FeedbackResponse
from app.schemas.incident import (
    IncidentDetailResponse,
    IncidentResponse,
    IncidentStatusUpdate,
)
from app.services.audit_service import audit_service

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get(
    "",
    response_model=PaginatedResponse[IncidentResponse],
    summary="List and Filter Incidents",
)
def list_incidents(
    store_id: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    safety_only: bool = Query(default=False),
    allergen_only: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[IncidentResponse]:
    """List consolidated incidents with filtering by store, category, severity, and policy flags."""
    query = db.query(Incident)

    # Store manager access restriction
    if current_user.role == UserRole.STORE_MANAGER:
        if not current_user.store_id:
            query = query.filter(Incident.store_id == "NONE")
        else:
            query = query.filter(Incident.store_id == current_user.store_id)
    elif store_id:
        query = query.filter(Incident.store_id == store_id)

    if category:
        query = query.filter(Incident.category == category)
    if severity:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)
    if safety_only:
        query = query.filter(Incident.safety_flag == True)
    if allergen_only:
        query = query.filter(Incident.allergen_flag == True)

    total = query.count()
    items = (
        query.order_by(Incident.last_seen_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedResponse(
        items=[IncidentResponse.model_validate(inc) for inc in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentDetailResponse,
    summary="Get Incident Details with Source Feedback",
)
def get_incident(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IncidentDetailResponse:
    """Retrieve an incident with all linked raw feedback records preserving full traceability."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise EntityNotFoundError("Incident", incident_id)

    check_store_access(current_user, incident.store_id)

    # Fetch source feedback
    source_records = (
        db.query(FeedbackRecord)
        .filter(FeedbackRecord.incident_id == incident.id)
        .order_by(FeedbackRecord.event_timestamp.desc())
        .all()
    )

    resp = IncidentDetailResponse.model_validate(incident)
    resp.source_feedback = [FeedbackResponse.model_validate(fb) for fb in source_records]
    return resp


@router.get(
    "/{incident_id}/feedback",
    response_model=List[FeedbackResponse],
    summary="Get Source Feedback for Incident",
)
def get_incident_feedback(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[FeedbackResponse]:
    """Retrieve only the raw feedback records linked to this incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise EntityNotFoundError("Incident", incident_id)

    check_store_access(current_user, incident.store_id)

    source_records = (
        db.query(FeedbackRecord)
        .filter(FeedbackRecord.incident_id == incident.id)
        .order_by(FeedbackRecord.event_timestamp.desc())
        .all()
    )
    return [FeedbackResponse.model_validate(fb) for fb in source_records]


@router.patch(
    "/{incident_id}/status",
    response_model=IncidentResponse,
    summary="Update Incident Status",
)
def update_incident_status(
    incident_id: str,
    status_in: IncidentStatusUpdate,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STORE_MANAGER])),
    db: Session = Depends(get_db),
) -> IncidentResponse:
    """Update incident lifecycle status (OPEN, UNDER_INVESTIGATION, RESOLVED, DISMISSED)."""
    if status_in.status not in IncidentStatus.ALL:
        raise InvalidInputError(f"Invalid status '{status_in.status}'. Allowed: {IncidentStatus.ALL}")

    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise EntityNotFoundError("Incident", incident_id)

    check_store_access(current_user, incident.store_id)

    old_status = incident.status
    incident.status = status_in.status
    db.commit()
    db.refresh(incident)

    audit_service.log_event(
        db=db,
        action=AuditAction.INCIDENT_STATUS_UPDATED,
        resource_type="Incident",
        resource_id=incident.id,
        actor=current_user,
        details={
            "old_status": old_status,
            "new_status": incident.status,
            "notes": status_in.notes,
        },
    )

    return IncidentResponse.model_validate(incident)

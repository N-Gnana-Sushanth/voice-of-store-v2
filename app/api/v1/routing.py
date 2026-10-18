"""Owning-function routing, triage, and human-review queue API endpoints."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError, InvalidInputError
from app.core.taxonomy import taxonomy_manager
from app.models.incident import Incident, IncidentStatus, OwningFunction
from app.models.store import Store
from app.models.user import User

router = APIRouter(prefix="/routing", tags=["Owning Function Routing"])


class ReassignOwnerRequest(BaseModel):
    new_owner: str = Field(..., description="Target owning department")
    reason: str = Field(..., min_length=3, description="Operational justification for reassignment")
    secondary_owner: Optional[str] = Field(default=None, description="Optional secondary owning department")
    mark_review_complete: bool = Field(default=True, description="Clear needs_human_review flag")


class RoutingPolicyResponse(BaseModel):
    departments: List[str]
    categories: List[Dict[str, Any]]


class IncidentRoutingItem(BaseModel):
    id: str
    store_id: str
    store_name: Optional[str] = None
    store_region: Optional[str] = None
    category: str
    severity: str
    status: str
    primary_owner: str
    secondary_owner: Optional[str] = None
    needs_human_review: bool
    actionability_score: float
    evidence_summary: Optional[str] = None
    feedback_count: int
    first_seen_at: datetime
    last_seen_at: datetime
    routing_history: Optional[List[Dict[str, Any]]] = None

    model_config = {"from_attributes": True}


class DepartmentAssignmentGroup(BaseModel):
    department: str
    total_assigned: int
    open_count: int
    needs_review_count: int
    critical_count: int
    incidents: List[IncidentRoutingItem]


@router.get("/policy", summary="Get Routing Policy and Taxonomy Rules")
def get_routing_policy(
    current_user: User = Depends(get_current_user),
) -> RoutingPolicyResponse:
    """Return configured owning functions, domain rules, and taxonomy assignments."""
    categories_data = [
        {
            "code": c.code,
            "name": c.name,
            "domain": c.domain,
            "primary_owner": c.primary_owner,
            "secondary_owner": c.secondary_owner,
            "default_severity": c.default_severity,
            "sla_hours": c.sla_hours,
        }
        for c in taxonomy_manager.list_all()
    ]
    return RoutingPolicyResponse(
        departments=OwningFunction.ALL,
        categories=categories_data,
    )


@router.get("/assignments", summary="List Incidents Grouped by Owning Function")
def get_routing_assignments(
    department: Optional[str] = Query(default=None, description="Filter to single department"),
    needs_review_only: bool = Query(default=False, description="Filter only to unclassified/uncertain incidents"),
    region: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[DepartmentAssignmentGroup]:
    """Retrieve active incidents grouped by their responsible department."""
    target_departments = [department] if department and department in OwningFunction.ALL else OwningFunction.ALL

    # Base query for active incidents
    query = (
        db.query(Incident, Store)
        .join(Store, Incident.store_id == Store.id)
        .filter(Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.UNDER_INVESTIGATION]))
    )

    if region and region != "All":
        query = query.filter(Store.region == region)

    if needs_review_only:
        query = query.filter(Incident.needs_human_review == True)

    results = query.order_by(Incident.last_seen_at.desc()).all()

    # Organize by department
    dept_map: Dict[str, List[IncidentRoutingItem]] = {d: [] for d in target_departments}

    for inc, store in results:
        owner = inc.primary_owner or OwningFunction.STORE_OPS
        if owner not in dept_map and not department:
            dept_map[owner] = []

        if owner in dept_map:
            item = IncidentRoutingItem(
                id=inc.id,
                store_id=inc.store_id,
                store_name=store.name,
                store_region=store.region,
                category=inc.category,
                severity=inc.severity,
                status=inc.status,
                primary_owner=owner,
                secondary_owner=inc.secondary_owner,
                needs_human_review=inc.needs_human_review,
                actionability_score=inc.actionability_score or 0.85,
                evidence_summary=inc.evidence_summary,
                feedback_count=inc.feedback_count,
                first_seen_at=inc.first_seen_at,
                last_seen_at=inc.last_seen_at,
                routing_history=inc.routing_history,
            )
            dept_map[owner].append(item)

    groups: List[DepartmentAssignmentGroup] = []
    for dept in target_departments:
        inc_list = dept_map.get(dept, [])
        groups.append(
            DepartmentAssignmentGroup(
                department=dept,
                total_assigned=len(inc_list),
                open_count=sum(1 for i in inc_list if i.status == IncidentStatus.OPEN),
                needs_review_count=sum(1 for i in inc_list if i.needs_human_review),
                critical_count=sum(1 for i in inc_list if i.severity == "CRITICAL"),
                incidents=inc_list,
            )
        )

    return groups


@router.patch("/incidents/{incident_id}/reassign", response_model=IncidentRoutingItem, summary="Reassign Incident to Different Department")
def reassign_incident(
    incident_id: str,
    request: ReassignOwnerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentRoutingItem:
    """Reassign an incident to a new department with audit logging."""
    if request.new_owner not in OwningFunction.ALL:
        raise InvalidInputError(f"Invalid department. Must be one of: {', '.join(OwningFunction.ALL)}")

    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise EntityNotFoundError("Incident", incident_id)

    store = db.query(Store).filter(Store.id == incident.store_id).first()

    history = incident.routing_history or []
    history.append({
        "action": "MANUAL_REASSIGNMENT",
        "previous_owner": incident.primary_owner,
        "new_owner": request.new_owner,
        "reason": request.reason,
        "user": current_user.email,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    incident.primary_owner = request.new_owner
    if request.secondary_owner:
        incident.secondary_owner = request.secondary_owner
    if request.mark_review_complete:
        incident.needs_human_review = False
    incident.routing_history = history

    db.commit()
    db.refresh(incident)

    return IncidentRoutingItem(
        id=incident.id,
        store_id=incident.store_id,
        store_name=store.name if store else None,
        store_region=store.region if store else None,
        category=incident.category,
        severity=incident.severity,
        status=incident.status,
        primary_owner=incident.primary_owner,
        secondary_owner=incident.secondary_owner,
        needs_human_review=incident.needs_human_review,
        actionability_score=incident.actionability_score or 0.85,
        evidence_summary=incident.evidence_summary,
        feedback_count=incident.feedback_count,
        first_seen_at=incident.first_seen_at,
        last_seen_at=incident.last_seen_at,
        routing_history=incident.routing_history,
    )

"""Escalation Precision Analytics and Human Review API endpoints."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError
from app.models.escalation_review import EscalationReview
from app.models.incident import Incident, IncidentSeverity
from app.models.store import Store
from app.models.user import User
from app.services.precision_service import precision_service

router = APIRouter(prefix="/analytics/escalation-precision", tags=["Escalation Precision Analytics"])


class ReviewSubmissionRequest(BaseModel):
    incident_id: str = Field(..., description="ID of escalated incident under review")
    is_truly_actionable: bool = Field(..., description="True if verified True Positive; False if False Positive")
    review_notes: Optional[str] = Field(default=None, description="Explanation or operational context for audit trail")


class EscalationQueueItem(BaseModel):
    incident_id: str
    store_id: str
    store_name: Optional[str] = None
    store_region: Optional[str] = None
    category: str
    severity: str
    policy_escalation_reason: Optional[str] = None
    evidence_summary: Optional[str] = None
    first_seen_at: datetime
    feedback_count: int
    is_reviewed: bool
    is_truly_actionable: Optional[bool] = None
    review_notes: Optional[str] = None

    model_config = {"from_attributes": True}


@router.get("", summary="Get Escalation Precision Metrics")
def get_escalation_precision_metrics(
    start_date: Optional[datetime] = Query(default=None, description="Evaluation window start (UTC)"),
    end_date: Optional[datetime] = Query(default=None, description="Evaluation window end (UTC)"),
    region: Optional[str] = Query(default=None, description="Filter by store region"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Returns true escalation precision = TP / (TP + FP).
    Unreviewed cases are explicitly isolated to prevent denominator distortion.
    Includes Wilson score 95% confidence intervals and statistical limitations.
    """
    return precision_service.get_precision_metrics(
        db=db,
        start_date=start_date,
        end_date=end_date,
        region=region,
    )


@router.get("/queue", response_model=List[EscalationQueueItem], summary="Get Escalation Review Queue")
def get_escalation_review_queue(
    status_filter: Optional[str] = Query(default="unreviewed", description="'unreviewed', 'reviewed', or 'all'"),
    region: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[EscalationQueueItem]:
    """Retrieve escalated incidents for human ground-truth validation."""
    query = (
        db.query(Incident, Store, EscalationReview)
        .join(Store, Incident.store_id == Store.id)
        .outerjoin(EscalationReview, Incident.id == EscalationReview.incident_id)
        .filter(Incident.policy_escalated == True)
    )

    if region and region != "All":
        query = query.filter(Store.region == region)

    if status_filter == "unreviewed":
        query = query.filter(
            (EscalationReview.id == None) | (EscalationReview.is_truly_actionable == None)
        )
    elif status_filter == "reviewed":
        query = query.filter(EscalationReview.is_truly_actionable != None)

    results = query.order_by(Incident.last_seen_at.desc()).limit(limit).all()

    items = []
    for inc, store, review in results:
        is_rev = review is not None and review.is_truly_actionable is not None
        items.append(
            EscalationQueueItem(
                incident_id=inc.id,
                store_id=inc.store_id,
                store_name=store.name,
                store_region=store.region,
                category=inc.category,
                severity=inc.severity,
                policy_escalation_reason=inc.policy_escalation_reason,
                evidence_summary=inc.evidence_summary,
                first_seen_at=inc.first_seen_at,
                feedback_count=inc.feedback_count,
                is_reviewed=is_rev,
                is_truly_actionable=review.is_truly_actionable if review else None,
                review_notes=review.review_notes if review else None,
            )
        )

    return items


@router.post("/review", status_code=status.HTTP_200_OK, summary="Record Ground-Truth Human Review")
def submit_escalation_review(
    req: ReviewSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Record human verification of whether an escalation was a True or False Positive."""
    review = precision_service.record_review(
        db=db,
        incident_id=req.incident_id,
        is_truly_actionable=req.is_truly_actionable,
        reviewer_id=current_user.id,
        review_notes=req.review_notes,
    )
    return {
        "status": "SUCCESS",
        "review_id": review.id,
        "incident_id": review.incident_id,
        "is_truly_actionable": review.is_truly_actionable,
        "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
    }

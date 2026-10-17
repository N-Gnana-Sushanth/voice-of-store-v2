"""Feedback ingestion and retrieval API endpoints."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import check_store_access, get_current_user, get_db
from app.core.exceptions import EntityNotFoundError
from app.models.feedback import FeedbackRecord
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse
from app.schemas.feedback import (
    FeedbackBatchResponse,
    FeedbackResponse,
    FeedbackSubmitBatch,
    FeedbackSubmitSingle,
)
from app.services.ingestion_service import ingestion_service

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Individual Feedback Record",
)
def submit_feedback(
    submission: FeedbackSubmitSingle,
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    """
    Ingest a single customer feedback or employee report.
    Executes the mandatory pipeline:
    Validation -> Preprocessing -> ML Classification -> Deduplication -> Safety Policy -> Persistence.
    Protected against duplicate submissions via client idempotency_key.
    """
    feedback, incident, res_status = ingestion_service.ingest_single(db, submission)
    return FeedbackResponse.model_validate(feedback)


@router.post(
    "/batch",
    response_model=FeedbackBatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Feedback Batch",
)
def submit_feedback_batch(
    batch: FeedbackSubmitBatch,
    db: Session = Depends(get_db),
) -> FeedbackBatchResponse:
    """
    Ingest up to 500 feedback records in a single batch.
    Uses independent transaction savepoints so a single failed record does not
    corrupt successfully committed records.
    """
    return ingestion_service.ingest_batch(db, batch)


@router.get(
    "",
    response_model=PaginatedResponse[FeedbackResponse],
    summary="List Feedback Records",
)
def list_feedback(
    store_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[FeedbackResponse]:
    """Retrieve raw feedback records with pagination, filtering, and store-level access control."""
    query = db.query(FeedbackRecord)

    # Store manager access restriction
    if current_user.role == UserRole.STORE_MANAGER:
        if not current_user.store_id:
            query = query.filter(FeedbackRecord.store_id == "NONE")
        else:
            query = query.filter(FeedbackRecord.store_id == current_user.store_id)
    elif store_id:
        query = query.filter(FeedbackRecord.store_id == store_id)

    if status:
        query = query.filter(FeedbackRecord.processing_status == status)

    total = query.count()
    items = (
        query.order_by(FeedbackRecord.event_timestamp.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedResponse(
        items=[FeedbackResponse.model_validate(fb) for fb in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Get Feedback Record by ID",
)
def get_feedback(
    feedback_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    """Retrieve single raw feedback record by identifier."""
    fb = db.query(FeedbackRecord).filter(FeedbackRecord.id == feedback_id).first()
    if not fb:
        raise EntityNotFoundError("FeedbackRecord", feedback_id)

    check_store_access(current_user, fb.store_id)
    return FeedbackResponse.model_validate(fb)

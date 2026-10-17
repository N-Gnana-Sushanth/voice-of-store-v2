"""Chronological replay and evaluation API endpoints."""

import math
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db, require_roles
from app.core.exceptions import EntityNotFoundError
from app.models.audit import AuditAction
from app.models.replay import ReplayRun
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse
from app.schemas.replay import (
    ReplayEvaluationMetrics,
    ReplayRunCreate,
    ReplayRunResponse,
)
from app.services.audit_service import audit_service
from app.services.replay_engine import replay_engine

router = APIRouter(prefix="/replay", tags=["Replay & Evaluation"])


@router.post(
    "",
    response_model=ReplayRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute Chronological Replay Run (Admin/Analyst)",
)
def create_replay_run(
    run_in: ReplayRunCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST])),
    db: Session = Depends(get_db),
) -> ReplayRunResponse:
    """
    Launch a deterministic chronological event-time replay experiment.
    Processes historical records strictly in event-time order to measure
    detection lead time, precision, recall, and confirm no future data leakage.
    Evaluates against 3 documented synthetic planted ground-truth incidents.
    """
    resp = replay_engine.run_replay(db=db, create_params=run_in)

    audit_service.log_event(
        db=db,
        action=AuditAction.REPLAY_STARTED,
        resource_type="ReplayRun",
        resource_id=resp.id,
        actor=current_user,
        details={
            "name": run_in.name,
            "start": run_in.time_range_start.isoformat(),
            "end": run_in.time_range_end.isoformat(),
        },
    )

    return resp


@router.get(
    "",
    response_model=PaginatedResponse[ReplayRunResponse],
    summary="List Replay Runs",
)
def list_replay_runs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST])),
    db: Session = Depends(get_db),
) -> PaginatedResponse[ReplayRunResponse]:
    """Retrieve historical replay runs with evaluation summaries."""
    query = db.query(ReplayRun)
    total = query.count()
    items = (
        query.order_by(ReplayRun.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    pages = math.ceil(total / limit) if total > 0 else 1

    formatted_items = []
    for r in items:
        metrics = None
        if r.evaluation_metrics_json:
            metrics = ReplayEvaluationMetrics.model_validate(r.evaluation_metrics_json)
        formatted_items.append(ReplayRunResponse(
            id=r.id,
            name=r.name,
            description=r.description,
            time_range_start=r.time_range_start,
            time_range_end=r.time_range_end,
            status=r.status,
            total_records=r.total_records,
            processed_records=r.processed_records,
            incidents_created=r.incidents_created,
            alerts_generated=r.alerts_generated,
            evaluation_metrics=metrics,
            model_version=r.model_version,
            baseline_version=r.baseline_version,
            start_time=r.start_time,
            completion_time=r.completion_time,
            error_message=r.error_message,
            created_at=r.created_at,
        ))

    return PaginatedResponse(
        items=formatted_items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/{replay_id}",
    response_model=ReplayRunResponse,
    summary="Get Replay Run Details & Evaluation Results",
)
def get_replay_run(
    replay_id: str,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST])),
    db: Session = Depends(get_db),
) -> ReplayRunResponse:
    """Retrieve full evaluation metrics, lead times, and planted incident results for a replay run."""
    r = db.query(ReplayRun).filter(ReplayRun.id == replay_id).first()
    if not r:
        raise EntityNotFoundError("ReplayRun", replay_id)

    metrics = None
    if r.evaluation_metrics_json:
        metrics = ReplayEvaluationMetrics.model_validate(r.evaluation_metrics_json)

    return ReplayRunResponse(
        id=r.id,
        name=r.name,
        description=r.description,
        time_range_start=r.time_range_start,
        time_range_end=r.time_range_end,
        status=r.status,
        total_records=r.total_records,
        processed_records=r.processed_records,
        incidents_created=r.incidents_created,
        alerts_generated=r.alerts_generated,
        evaluation_metrics=metrics,
        model_version=r.model_version,
        baseline_version=r.baseline_version,
        start_time=r.start_time,
        completion_time=r.completion_time,
        error_message=r.error_message,
        created_at=r.created_at,
    )

"""Remediation Task API endpoints for Action Queue."""

from datetime import datetime, timezone
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError, InvalidInputError
from app.models.audit import AuditAction
from app.models.task import RemediationTask, TaskStatus
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskStatusUpdate
from app.services.audit_service import audit_service

router = APIRouter(prefix="/tasks", tags=["Action Queue"])


@router.get(
    "",
    response_model=PaginatedResponse[TaskResponse],
    summary="List Remediation Tasks",
)
def list_tasks(
    status: Optional[str] = Query(default=None),
    department: Optional[str] = Query(default=None),
    store_id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[TaskResponse]:
    """Retrieve actionable remediation tasks with filtering by status and department."""
    query = db.query(RemediationTask)

    if status and status != "All":
        query = query.filter(RemediationTask.status == status)
    if department:
        query = query.filter(RemediationTask.owner == department)
    if store_id:
        query = query.filter(RemediationTask.store_id == store_id)

    total = query.count()
    items = (
        query.order_by(RemediationTask.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedResponse(
        items=[TaskResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Update Task Status",
)
def update_task_status(
    task_id: str,
    status_in: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Update task lifecycle status (Open, In Progress, Resolved)."""
    if status_in.status not in TaskStatus.ALL:
        raise InvalidInputError(f"Invalid status '{status_in.status}'. Allowed: {TaskStatus.ALL}")

    task = (
        db.query(RemediationTask)
        .filter((RemediationTask.id == task_id) | (RemediationTask.task_id == task_id))
        .first()
    )
    if not task:
        raise EntityNotFoundError("RemediationTask", task_id)

    old_status = task.status
    task.status = status_in.status
    if status_in.notes:
        task.notes = status_in.notes
    if status_in.status == TaskStatus.RESOLVED:
        task.resolved_at = datetime.now(timezone.utc)
    else:
        task.resolved_at = None

    db.commit()
    db.refresh(task)

    audit_service.log_event(
        db=db,
        action="TASK_STATUS_UPDATED",
        resource_type="RemediationTask",
        resource_id=task.id,
        actor=current_user,
        details={"old_status": old_status, "new_status": task.status, "task_id": task.task_id},
    )

    return TaskResponse.model_validate(task)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Remediation Task",
)
def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Create a new action task."""
    task = RemediationTask(
        task_id=task_in.task_id,
        title=task_in.title,
        store_id=task_in.store_id,
        store_name=task_in.store_name,
        owner=task_in.owner,
        owner_tag=task_in.owner_tag,
        severity=task_in.severity,
        status=task_in.status,
        sla_window=task_in.sla_window,
        sla_urgent=task_in.sla_urgent,
        reported_date=task_in.reported_date,
        notes=task_in.notes,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)

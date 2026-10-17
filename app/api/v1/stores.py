"""Store management API endpoints."""

import math
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import check_store_access, get_current_user, get_db, require_roles
from app.core.exceptions import DuplicateEntityError, EntityNotFoundError
from app.models.audit import AuditAction
from app.models.store import Store
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse
from app.schemas.store import StoreCreate, StoreResponse, StoreUpdate
from app.services.audit_service import audit_service

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.post(
    "",
    response_model=StoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Store (Admin Only)",
)
def create_store(
    store_in: StoreCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db),
) -> StoreResponse:
    """Create a new retail store with operational exposure parameters."""
    existing = db.query(Store).filter(Store.store_number == store_in.store_number).first()
    if existing:
        raise DuplicateEntityError("Store", store_in.store_number)

    store = Store(
        store_number=store_in.store_number,
        name=store_in.name,
        address=store_in.address,
        city=store_in.city,
        state=store_in.state,
        size_sqft=store_in.size_sqft,
        avg_daily_transactions=store_in.avg_daily_transactions,
        is_active=True,
    )
    db.add(store)
    db.commit()
    db.refresh(store)

    audit_service.log_event(
        db=db,
        action=AuditAction.STORE_CREATED,
        resource_type="Store",
        resource_id=store.id,
        actor=current_user,
        details={"store_number": store.store_number, "name": store.name},
    )

    return StoreResponse.model_validate(store)


@router.get(
    "",
    response_model=PaginatedResponse[StoreResponse],
    summary="List Stores",
)
def list_stores(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    is_active: Optional[bool] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[StoreResponse]:
    """Retrieve stores with pagination and active status filtering."""
    query = db.query(Store)

    # Store manager can only see their assigned store
    if current_user.role == UserRole.STORE_MANAGER:
        if current_user.store_id:
            query = query.filter(Store.id == current_user.store_id)
        else:
            query = query.filter(Store.id == "NONE")

    if is_active is not None:
        query = query.filter(Store.is_active == is_active)

    total = query.count()
    items = query.order_by(Store.store_number.asc()).offset((page - 1) * limit).limit(limit).all()
    pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedResponse(
        items=[StoreResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/{store_id}",
    response_model=StoreResponse,
    summary="Get Store by ID",
)
def get_store(
    store_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StoreResponse:
    """Retrieve details for a specific store with store-level access enforcement."""
    store = (
        db.query(Store)
        .filter((Store.id == store_id) | (Store.store_number == store_id))
        .first()
    )
    if not store:
        raise EntityNotFoundError("Store", store_id)

    check_store_access(current_user, store.id)
    return StoreResponse.model_validate(store)


@router.patch(
    "/{store_id}",
    response_model=StoreResponse,
    summary="Update Store Metadata (Admin Only)",
)
def update_store(
    store_id: str,
    store_in: StoreUpdate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db),
) -> StoreResponse:
    """Update store details, floor area, or baseline exposure transactions."""
    store = (
        db.query(Store)
        .filter((Store.id == store_id) | (Store.store_number == store_id))
        .first()
    )
    if not store:
        raise EntityNotFoundError("Store", store_id)

    update_data = store_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(store, field, val)

    db.commit()
    db.refresh(store)

    audit_service.log_event(
        db=db,
        action=AuditAction.STORE_UPDATED,
        resource_type="Store",
        resource_id=store.id,
        actor=current_user,
        details=update_data,
    )

    return StoreResponse.model_validate(store)

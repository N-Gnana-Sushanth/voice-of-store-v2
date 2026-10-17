"""Store analytics and peer comparison API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import check_store_access, get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.analytics import StoreComparisonItem, StoreSummaryAnalytics
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/summary",
    response_model=StoreSummaryAnalytics,
    summary="Get Store or Consolidated Analytics Summary",
)
def get_analytics_summary(
    store_id: Optional[str] = Query(default=None, description="Optional store ID; if omitted, returns all stores consolidated"),
    time_window_days: int = Query(default=30, ge=1, le=365, description="Time window in days (1 to 365)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StoreSummaryAnalytics:
    """
    Retrieve distinct incident analytics, category breakdowns, severity distributions,
    and exposure-normalized rates per 1,000 transactions.
    """
    # Store manager can only request analytics for their own store
    target_store_id = store_id
    if current_user.role == UserRole.STORE_MANAGER:
        target_store_id = current_user.store_id

    if target_store_id:
        check_store_access(current_user, target_store_id)

    return analytics_service.get_store_analytics(
        db=db,
        store_id=target_store_id,
        time_window_days=time_window_days,
    )


@router.get(
    "/comparisons",
    response_model=List[StoreComparisonItem],
    summary="Get Exposure-Normalized Store Comparisons",
)
def get_store_comparisons(
    time_window_days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[StoreComparisonItem]:
    """
    Retrieve fair side-by-side store comparisons normalized by customer transaction volume.
    Prevents erroneous raw count comparisons between small and large stores.
    """
    # If store manager, return list filtered to their store
    comparisons = analytics_service.get_store_comparisons(
        db=db,
        time_window_days=time_window_days,
    )
    if current_user.role == UserRole.STORE_MANAGER:
        comparisons = [c for c in comparisons if c.store_id == current_user.store_id]

    return comparisons

"""Regional Brief API endpoints for weekly one-page briefs and executive views."""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError
from app.models.regional_brief import RegionalBrief
from app.models.store import Store
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.services.regional_brief_service import regional_brief_service

router = APIRouter(prefix="/regional-briefs", tags=["Regional Briefs"])


class RegionalBriefGenerateRequest(BaseModel):
    region: str = Field(..., description="Target region (e.g. North, South, East, West)")
    as_of_date: Optional[datetime] = Field(default=None, description="Optional end of 7-day period (UTC)")


class RegionalBriefSummaryResponse(BaseModel):
    id: str
    region: str
    week_start: datetime
    week_end: datetime
    executive_summary: str
    top_issues_count: int
    total_feedback: int
    incident_count: int
    generated_at: datetime

    model_config = {"from_attributes": True}


class RegionalBriefDetailResponse(BaseModel):
    id: str
    region: str
    week_start: datetime
    week_end: datetime
    executive_summary: str
    top_issues_json: List[Dict[str, Any]]
    low_volume_safety_json: List[Dict[str, Any]]
    metrics_json: Dict[str, Any]
    html_content: Optional[str] = None
    generated_at: datetime

    model_config = {"from_attributes": True}


@router.get("/regions", summary="List Available Regions")
def list_regions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[str]:
    """Return all unique active regions from stores."""
    results = (
        db.query(Store.region)
        .filter(Store.is_active == True, Store.region.isnot(None))
        .distinct()
        .all()
    )
    regions = sorted(list({r[0] for r in results if r[0]}))
    if not regions:
        regions = ["North", "South", "East", "West"]
    return regions


@router.get("", response_model=PaginatedResponse[RegionalBriefDetailResponse], summary="List Regional Briefs")
def list_regional_briefs(
    region: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[RegionalBriefDetailResponse]:
    """Retrieve archived regional briefs with optional region filter."""
    query = db.query(RegionalBrief)
    if region and region != "All":
        query = query.filter(RegionalBrief.region == region)

    total = query.count()
    items = (
        query.order_by(RegionalBrief.week_end.desc(), RegionalBrief.generated_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return PaginatedResponse(
        items=[RegionalBriefDetailResponse.model_validate(b) for b in items],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total > 0 else 0,
    )


@router.get("/{region}/latest", response_model=RegionalBriefDetailResponse, summary="Get Latest Regional Brief")
def get_latest_regional_brief(
    region: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RegionalBriefDetailResponse:
    """Retrieve the most recent brief for a region, or auto-generate if none exists."""
    brief = (
        db.query(RegionalBrief)
        .filter(RegionalBrief.region == region)
        .order_by(RegionalBrief.week_end.desc(), RegionalBrief.generated_at.desc())
        .first()
    )
    if not brief:
        # Generate on-demand
        brief = regional_brief_service.generate_brief(db=db, region=region)

    return RegionalBriefDetailResponse.model_validate(brief)


@router.get("/{brief_id}", response_model=RegionalBriefDetailResponse, summary="Get Regional Brief By ID")
def get_regional_brief_by_id(
    brief_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RegionalBriefDetailResponse:
    brief = db.query(RegionalBrief).filter(RegionalBrief.id == brief_id).first()
    if not brief:
        raise EntityNotFoundError("RegionalBrief", brief_id)
    return RegionalBriefDetailResponse.model_validate(brief)


@router.get("/{brief_id}/html", summary="Get One-Page Printable HTML")
def get_regional_brief_html(
    brief_id: str,
    db: Session = Depends(get_db),
) -> Response:
    """Returns standalone single-page printable HTML format for PDF or direct printing."""
    brief = db.query(RegionalBrief).filter(RegionalBrief.id == brief_id).first()
    if not brief:
        raise EntityNotFoundError("RegionalBrief", brief_id)
    return Response(content=brief.html_content or "<html><body>No HTML available</body></html>", media_type="text/html")


@router.post("/generate", response_model=RegionalBriefDetailResponse, status_code=status.HTTP_201_CREATED, summary="Generate New Regional Brief")
def generate_regional_brief(
    request: RegionalBriefGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RegionalBriefDetailResponse:
    """Explicitly trigger generation of a new 7-day brief for a region."""
    brief = regional_brief_service.generate_brief(
        db=db,
        region=request.region,
        as_of_date=request.as_of_date,
    )
    return RegionalBriefDetailResponse.model_validate(brief)

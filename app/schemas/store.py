"""Store request and response schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StoreBase(BaseModel):
    store_number: str = Field(..., min_length=2, max_length=50, description="Unique store code")
    name: str = Field(..., min_length=2, max_length=255)
    address: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=50)
    size_sqft: float = Field(default=10000.0, gt=0, description="Store retail floor area")
    avg_daily_transactions: float = Field(default=1500.0, gt=0, description="Baseline daily transaction volume for exposure normalization")


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    size_sqft: Optional[float] = Field(default=None, gt=0)
    avg_daily_transactions: Optional[float] = Field(default=None, gt=0)
    is_active: Optional[bool] = None


class StoreResponse(StoreBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

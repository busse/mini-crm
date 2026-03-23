"""Deal schemas.

Pydantic models for deal request/response validation.
"""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DealCreate(BaseModel):
    """Fields for creating a deal."""

    title: str
    value: Decimal
    currency: str = "USD"
    expected_close: date | None = None
    contact_id: int
    stage_id: int


class DealUpdate(BaseModel):
    """Fields for updating a deal (all optional)."""

    title: str | None = None
    value: Decimal | None = None
    currency: str | None = None
    expected_close: date | None = None
    contact_id: int | None = None
    stage_id: int | None = None


class DealStageUpdate(BaseModel):
    """Fields for updating a deal's stage."""

    stage_id: int


class TagResponse(BaseModel):
    """Tag response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str | None


class DealResponse(BaseModel):
    """Deal response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    value: Decimal | None
    currency: str
    expected_close: date | None
    contact_id: int | None
    contact_name: str | None = None
    stage_id: int
    stage_name: str | None = None
    tags: list[TagResponse] = []
    activity_count: int = 0
    created_at: datetime
    updated_at: datetime


class DealListResponse(BaseModel):
    """Paginated list of deals."""

    items: list[DealResponse]
    total: int
    page: int
    per_page: int

"""Deal schemas.

Pydantic models for deal request/response validation.
"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class DealBase(BaseModel):
    """Base deal fields."""

    title: str
    value: Decimal | None = None
    stage_id: int
    contact_id: int | None = None
    company_id: int | None = None
    expected_close_date: datetime | None = None
    notes: str | None = None


class DealCreate(DealBase):
    """Fields for creating a deal."""

    pass


class DealUpdate(BaseModel):
    """Fields for updating a deal (all optional)."""

    title: str | None = None
    value: Decimal | None = None
    stage_id: int | None = None
    contact_id: int | None = None
    company_id: int | None = None
    expected_close_date: datetime | None = None
    notes: str | None = None


class DealResponse(DealBase):
    """Deal response with ID and timestamps."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True

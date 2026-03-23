"""Company schemas.

Pydantic models for company request/response validation.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    """Fields for creating a company."""

    name: str
    industry: str | None = None
    website: str | None = None


class CompanyUpdate(BaseModel):
    """Fields for updating a company (all optional)."""

    name: str | None = None
    industry: str | None = None
    website: str | None = None


class ContactBrief(BaseModel):
    """Brief contact info for embedding in company response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str | None


class CompanyResponse(BaseModel):
    """Company response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    industry: str | None
    website: str | None
    contact_count: int
    created_at: datetime
    updated_at: datetime


class CompanyDetailResponse(CompanyResponse):
    """Company response with list of contacts."""

    contacts: list[ContactBrief]


class CompanyListResponse(BaseModel):
    """Paginated list of companies."""

    items: list[CompanyResponse]
    total: int
    page: int
    per_page: int

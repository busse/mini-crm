"""Company schemas.

Pydantic models for company request/response validation.
"""
from pydantic import BaseModel


class CompanyBase(BaseModel):
    """Base company fields."""

    name: str
    website: str | None = None
    industry: str | None = None
    notes: str | None = None


class CompanyCreate(CompanyBase):
    """Fields for creating a company."""

    pass


class CompanyUpdate(BaseModel):
    """Fields for updating a company (all optional)."""

    name: str | None = None
    website: str | None = None
    industry: str | None = None
    notes: str | None = None


class CompanyResponse(CompanyBase):
    """Company response with ID."""

    id: int

    class Config:
        from_attributes = True

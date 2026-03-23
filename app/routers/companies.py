"""Companies router.

CRUD endpoints for managing companies.
Routes: GET/POST /api/companies, GET/PUT/DELETE /api/companies/{id}
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("")
def list_companies():
    """List companies with pagination."""
    pass


@router.post("")
def create_company():
    """Create a new company."""
    pass


@router.get("/{company_id}")
def get_company(company_id: int):
    """Get a single company by ID."""
    pass


@router.put("/{company_id}")
def update_company(company_id: int):
    """Update a company."""
    pass


@router.delete("/{company_id}")
def delete_company(company_id: int):
    """Delete a company."""
    pass

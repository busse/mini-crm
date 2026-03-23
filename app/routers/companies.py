"""Companies router.

CRUD endpoints for managing companies.
Routes: GET/POST /api/companies, GET/PUT /api/companies/{id}
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.company import Company
from app.models.user import User
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyDetailResponse,
    CompanyListResponse,
    ContactBrief,
)

router = APIRouter(prefix="/api/companies", tags=["companies"])


def _company_to_response(company: Company) -> CompanyResponse:
    """Convert Company model to response schema with contact count."""
    return CompanyResponse(
        id=company.id,
        name=company.name,
        industry=company.industry,
        website=company.website,
        contact_count=len(company.contacts),
        created_at=company.created_at,
        updated_at=company.updated_at,
    )


def _company_to_detail_response(company: Company) -> CompanyDetailResponse:
    """Convert Company model to detail response with contacts list."""
    return CompanyDetailResponse(
        id=company.id,
        name=company.name,
        industry=company.industry,
        website=company.website,
        contact_count=len(company.contacts),
        created_at=company.created_at,
        updated_at=company.updated_at,
        contacts=[
            ContactBrief(
                id=c.id,
                first_name=c.first_name,
                last_name=c.last_name,
                email=c.email,
            )
            for c in company.contacts
        ],
    )


@router.get("", response_model=CompanyListResponse)
def list_companies(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
) -> CompanyListResponse:
    """List companies with pagination."""
    offset = (page - 1) * per_page
    total = db.query(Company).count()
    companies = (
        db.query(Company)
        .options(joinedload(Company.contacts))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return CompanyListResponse(
        items=[_company_to_response(c) for c in companies],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{company_id}", response_model=CompanyDetailResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
) -> CompanyDetailResponse:
    """Get a single company by ID with contacts."""
    company = (
        db.query(Company)
        .options(joinedload(Company.contacts))
        .filter(Company.id == company_id)
        .first()
    )
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    return _company_to_detail_response(company)


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_in: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyResponse:
    """Create a new company."""
    company = Company(
        name=company_in.name,
        industry=company_in.industry,
        website=company_in.website,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return _company_to_response(company)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyResponse:
    """Update a company."""
    company = (
        db.query(Company)
        .options(joinedload(Company.contacts))
        .filter(Company.id == company_id)
        .first()
    )
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    update_data = company_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return _company_to_response(company)

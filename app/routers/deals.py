"""Deals router.

CRUD endpoints for managing deals.
Routes: GET/POST /api/deals, GET/PUT /api/deals/{id}, PATCH /api/deals/{id}/stage
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.deal import Deal
from app.models.user import User
from app.schemas.deal import (
    DealCreate,
    DealUpdate,
    DealStageUpdate,
    DealResponse,
    DealListResponse,
    TagResponse,
)
from app.services.deal_service import move_to_stage

router = APIRouter(prefix="/api/deals", tags=["deals"])


def _deal_to_response(deal: Deal) -> DealResponse:
    """Convert Deal model to response schema with related data."""
    contact_name = None
    if deal.contact:
        contact_name = f"{deal.contact.first_name} {deal.contact.last_name}"

    return DealResponse(
        id=deal.id,
        title=deal.title,
        value=deal.value,
        currency=deal.currency,
        expected_close=deal.expected_close,
        contact_id=deal.contact_id,
        contact_name=contact_name,
        stage_id=deal.stage_id,
        stage_name=deal.stage.name if deal.stage else None,
        tags=[TagResponse.model_validate(t) for t in deal.tags],
        activity_count=len(deal.activities),
        created_at=deal.created_at,
        updated_at=deal.updated_at,
    )


@router.get("", response_model=DealListResponse)
def list_deals(
    page: int = 1,
    per_page: int = 20,
    stage_id: int | None = None,
    db: Session = Depends(get_db),
) -> DealListResponse:
    """List deals with pagination and optional stage filter."""
    query = db.query(Deal)

    if stage_id is not None:
        query = query.filter(Deal.stage_id == stage_id)

    total = query.count()
    offset = (page - 1) * per_page
    # N+1 query pattern: lazy loading triggers separate queries per deal
    deals = query.offset(offset).limit(per_page).all()
    return DealListResponse(
        items=[_deal_to_response(d) for d in deals],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: int,
    db: Session = Depends(get_db),
) -> DealResponse:
    """Get a single deal by ID with contact, stage, activities, and tags."""
    deal = (
        db.query(Deal)
        .options(
            joinedload(Deal.contact),
            joinedload(Deal.stage),
            joinedload(Deal.tags),
            joinedload(Deal.activities),
        )
        .filter(Deal.id == deal_id)
        .first()
    )
    if deal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return _deal_to_response(deal)


@router.post("", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
def create_deal(
    deal_in: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DealResponse:
    """Create a new deal."""
    deal = Deal(
        title=deal_in.title,
        value=deal_in.value,
        currency=deal_in.currency,
        expected_close=deal_in.expected_close,
        contact_id=deal_in.contact_id,
        stage_id=deal_in.stage_id,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)

    deal = (
        db.query(Deal)
        .options(
            joinedload(Deal.contact),
            joinedload(Deal.stage),
            joinedload(Deal.tags),
            joinedload(Deal.activities),
        )
        .filter(Deal.id == deal.id)
        .first()
    )
    return _deal_to_response(deal)


@router.put("/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: int,
    deal_in: DealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DealResponse:
    """Update a deal."""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    update_data = deal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deal, field, value)

    db.commit()
    db.refresh(deal)

    deal = (
        db.query(Deal)
        .options(
            joinedload(Deal.contact),
            joinedload(Deal.stage),
            joinedload(Deal.tags),
            joinedload(Deal.activities),
        )
        .filter(Deal.id == deal.id)
        .first()
    )
    return _deal_to_response(deal)


@router.patch("/{deal_id}/stage", response_model=DealResponse)
def update_deal_stage(
    deal_id: int,
    stage_update: DealStageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DealResponse:
    """Move a deal to a new stage."""
    deal = move_to_stage(db, deal_id, stage_update.stage_id)

    deal = (
        db.query(Deal)
        .options(
            joinedload(Deal.contact),
            joinedload(Deal.stage),
            joinedload(Deal.tags),
            joinedload(Deal.activities),
        )
        .filter(Deal.id == deal.id)
        .first()
    )
    return _deal_to_response(deal)

"""Pipeline router.

Endpoints for the kanban-style pipeline view.
Routes: GET /api/pipeline/stages
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.deal import Deal
from app.models.deal_stage import DealStage


router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


class StageWithCount(BaseModel):
    """Stage response with deal count."""

    id: int
    name: str
    display_order: int
    is_closed: bool
    deal_count: int

    model_config = {"from_attributes": True}


class StagesListResponse(BaseModel):
    """List of stages with counts."""

    items: list[StageWithCount]
    total: int


@router.get("/stages", response_model=StagesListResponse)
def list_stages(db: Session = Depends(get_db)) -> StagesListResponse:
    """List all pipeline stages with deal counts."""
    stages = (
        db.query(
            DealStage.id,
            DealStage.name,
            DealStage.display_order,
            DealStage.is_closed,
            func.count(Deal.id).label("deal_count"),
        )
        .outerjoin(Deal, Deal.stage_id == DealStage.id)
        .group_by(DealStage.id)
        .order_by(DealStage.display_order)
        .all()
    )

    items = [
        StageWithCount(
            id=s.id,
            name=s.name,
            display_order=s.display_order,
            is_closed=s.is_closed,
            deal_count=s.deal_count,
        )
        for s in stages
    ]

    return StagesListResponse(items=items, total=len(items))

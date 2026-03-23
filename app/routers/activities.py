"""Activities router.

Endpoints for managing deal activities.
Routes: GET/POST /api/deals/{deal_id}/activities
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.activity import Activity
from app.models.deal import Deal
from app.models.user import User
from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse,
    ActivityListResponse,
)

router = APIRouter(prefix="/api/deals", tags=["activities"])


@router.get("/{deal_id}/activities", response_model=ActivityListResponse)
def list_activities(
    deal_id: int,
    db: Session = Depends(get_db),
) -> ActivityListResponse:
    """List activities for a deal."""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    activities = (
        db.query(Activity)
        .filter(Activity.deal_id == deal_id)
        .order_by(Activity.occurred_at.desc())
        .all()
    )
    return ActivityListResponse(
        items=[ActivityResponse.model_validate(a) for a in activities],
        total=len(activities),
    )


@router.post(
    "/{deal_id}/activities",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    deal_id: int,
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActivityResponse:
    """Log a new activity on a deal."""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    activity = Activity(
        type=activity_in.type.value,
        subject=activity_in.subject,
        notes=activity_in.notes,
        occurred_at=activity_in.occurred_at,
        deal_id=deal_id,
        contact_id=deal.contact_id,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return ActivityResponse.model_validate(activity)

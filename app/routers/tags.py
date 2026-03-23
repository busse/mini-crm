"""Tags router.

Endpoints for managing tags and deal-tag associations.
Routes: GET /api/tags, POST/DELETE /api/deals/{deal_id}/tags
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.deal import Deal
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import (
    DealTagRequest,
    TagResponse,
    TagListResponse,
)

router = APIRouter(tags=["tags"])


@router.get("/api/tags", response_model=TagListResponse)
def list_tags(
    db: Session = Depends(get_db),
) -> TagListResponse:
    """List all tags."""
    tags = db.query(Tag).order_by(Tag.name).all()
    return TagListResponse(
        items=[TagResponse.model_validate(t) for t in tags],
        total=len(tags),
    )


@router.post(
    "/api/deals/{deal_id}/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_tag_to_deal(
    deal_id: int,
    tag_request: DealTagRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TagResponse:
    """Add a tag to a deal."""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )

    tag = db.query(Tag).filter(Tag.id == tag_request.tag_id).first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag in deal.tags:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag already attached to deal",
        )

    deal.tags.append(tag)
    db.commit()
    return TagResponse.model_validate(tag)


@router.delete(
    "/api/deals/{deal_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_tag_from_deal(
    deal_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove a tag from a deal."""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )

    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag not in deal.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not attached to deal",
        )

    deal.tags.remove(tag)
    db.commit()

"""Deal service.

Business logic for deal operations, including stage transitions.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.deal_stage import DealStage


def move_to_stage(db: Session, deal_id: int, new_stage_id: int) -> Deal:
    """Move a deal to a new stage.

    Validates the stage exists and updates the deal.

    Args:
        db: Database session.
        deal_id: ID of the deal to update.
        new_stage_id: ID of the target stage.

    Returns:
        The updated deal.

    Raises:
        HTTPException: If deal or stage is not found.
    """
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    stage = db.query(DealStage).filter(DealStage.id == new_stage_id).first()
    if stage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    deal.stage_id = new_stage_id
    db.commit()
    db.refresh(deal)

    # TODO: send notification when deal moves to Closed Won

    return deal


def get_pipeline_data(db: Session):
    """Get all deals grouped by stage for pipeline view."""
    pass


def calculate_pipeline_value(db: Session):
    """Calculate total value by stage."""
    pass

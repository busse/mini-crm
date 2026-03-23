"""Deal service.

Business logic for deal operations, including stage transitions.
"""
from sqlalchemy.orm import Session


def move_deal_to_stage(db: Session, deal_id: int, stage_id: int):
    """Move a deal to a new stage.

    Validates the stage transition and updates the deal.
    """
    pass


def get_pipeline_data(db: Session):
    """Get all deals grouped by stage for pipeline view."""
    pass


def calculate_pipeline_value(db: Session):
    """Calculate total value by stage."""
    pass

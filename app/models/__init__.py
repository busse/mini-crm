"""SQLAlchemy models.

Imports all models for Alembic autogenerate support.
"""
from app.models.user import User
from app.models.company import Company
from app.models.contact import Contact
from app.models.deal_stage import DealStage
from app.models.tag import Tag
from app.models.deal_tag import DealTag
from app.models.deal import Deal
from app.models.activity import Activity

__all__ = [
    "User",
    "Company",
    "Contact",
    "DealStage",
    "Tag",
    "DealTag",
    "Deal",
    "Activity",
]

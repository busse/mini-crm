"""DealTag model.

Join table for many-to-many relationship between deals and tags.
"""
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DealTag(Base):
    """Association table for Deal-Tag many-to-many relationship."""

    __tablename__ = "deal_tags"

    deal_id: Mapped[int] = mapped_column(
        ForeignKey("deals.id"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id"), primary_key=True
    )

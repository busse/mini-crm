"""Tag model.

Represents tags for categorizing deals.
"""
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.deal import Deal


class Tag(Base):
    """A tag for categorization."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    color: Mapped[str | None] = mapped_column(String(20))

    deals: Mapped[list["Deal"]] = relationship(
        "Deal", secondary="deal_tags", back_populates="tags"
    )

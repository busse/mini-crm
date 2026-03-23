"""DealStage model.

Represents stages in the sales pipeline (e.g., Lead, Qualified, Proposal, Won).
"""
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.deal import Deal


class DealStage(Base):
    """A stage in the sales pipeline."""

    __tablename__ = "deal_stages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)

    deals: Mapped[list["Deal"]] = relationship(
        "Deal", back_populates="stage"
    )

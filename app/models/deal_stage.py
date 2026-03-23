"""DealStage model.

Represents stages in the sales pipeline (e.g., Lead, Qualified, Proposal, Won).
"""
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DealStage(Base):
    """A stage in the sales pipeline."""

    __tablename__ = "deal_stages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[str | None] = mapped_column(String(20))

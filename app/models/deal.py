"""Deal model.

Represents sales opportunities/deals in the pipeline.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Numeric, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.deal_stage import DealStage
    from app.models.activity import Activity
    from app.models.tag import Tag


class Deal(Base):
    """A sales deal/opportunity."""

    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    expected_close: Mapped[date | None] = mapped_column(Date)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"))
    stage_id: Mapped[int] = mapped_column(ForeignKey("deal_stages.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    contact: Mapped["Contact | None"] = relationship(
        "Contact", back_populates="deals"
    )
    stage: Mapped["DealStage"] = relationship(
        "DealStage", back_populates="deals"
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="deal"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="deal_tags", back_populates="deals"
    )

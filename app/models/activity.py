"""Activity model.

Represents logged activities (calls, emails, meetings) on deals/contacts.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.deal import Deal


class Activity(Base):
    """A logged activity (call, email, meeting, note)."""

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))  # call, email, meeting, note
    subject: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime)
    deal_id: Mapped[int | None] = mapped_column(ForeignKey("deals.id"))
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    deal: Mapped["Deal | None"] = relationship(
        "Deal", back_populates="activities"
    )
    contact: Mapped["Contact | None"] = relationship(
        "Contact", back_populates="activities"
    )

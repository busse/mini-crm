"""Activity model.

Represents logged activities (calls, emails, meetings) on deals/contacts.
"""
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Activity(Base):
    """A logged activity (call, email, meeting, note)."""

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))  # call, email, meeting, note
    subject: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"))
    deal_id: Mapped[int | None] = mapped_column(ForeignKey("deals.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

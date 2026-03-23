"""Deal model.

Represents sales opportunities/deals in the pipeline.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Deal(Base):
    """A sales deal/opportunity."""

    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    stage_id: Mapped[int] = mapped_column(ForeignKey("deal_stages.id"))
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"))
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    expected_close_date: Mapped[datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

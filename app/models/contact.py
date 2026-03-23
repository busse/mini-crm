"""Contact model.

Represents individual people/contacts in the CRM.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.deal import Deal
    from app.models.activity import Activity


class Contact(Base):
    """A person/contact, optionally associated with a company."""

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    role: Mapped[str | None] = mapped_column(String(100))
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    company: Mapped["Company | None"] = relationship(
        "Company", back_populates="contacts"
    )
    deals: Mapped[list["Deal"]] = relationship(
        "Deal", back_populates="contact"
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="contact"
    )

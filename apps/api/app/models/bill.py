from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.household import Household


class Bill(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "bills"
    __table_args__ = (
        CheckConstraint("length(name) > 0", name="name_not_empty"),
        CheckConstraint("amount_php > 0", name="amount_php_positive"),
        CheckConstraint(
            "status IN ('scheduled', 'paid', 'skipped')",
            name="status_valid",
        ),
        Index("ix_bills_household_id_due_date", "household_id", "due_date"),
        Index("ix_bills_status", "status"),
    )

    household_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    amount_php: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    recurring: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    recurrence_rule: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="scheduled",
        server_default="scheduled",
    )

    household: Mapped[Household] = relationship(back_populates="bills")

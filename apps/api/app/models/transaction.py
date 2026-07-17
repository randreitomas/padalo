from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.envelope import Envelope
    from app.models.household import Household
    from app.models.membership import HouseholdMember


class Transaction(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount_php > 0", name="amount_php_positive"),
        CheckConstraint(
            "transaction_type IN ('expense', 'refund', 'adjustment')",
            name="transaction_type_valid",
        ),
        CheckConstraint("source IN ('manual', 'chat', 'receipt')", name="source_valid"),
        Index("ix_transactions_household_id_created_at", "household_id", "created_at"),
        Index("ix_transactions_envelope_id_created_at", "envelope_id", "created_at"),
        Index("ix_transactions_logged_by_member_id", "logged_by_member_id"),
    )

    household_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
    )
    envelope_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("envelopes.id", ondelete="SET NULL"),
        nullable=True,
    )
    logged_by_member_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("household_members.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount_php: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="expense",
        server_default="expense",
    )
    source: Mapped[str] = mapped_column(
        String(24), nullable=False, default="manual", server_default="manual"
    )
    merchant: Mapped[str | None] = mapped_column(String(160), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    occurred_on: Mapped[date] = mapped_column(Date, nullable=False)

    household: Mapped[Household] = relationship(back_populates="transactions")
    envelope: Mapped[Envelope | None] = relationship(back_populates="transactions")
    logged_by_member: Mapped[HouseholdMember | None] = relationship(back_populates="transactions")

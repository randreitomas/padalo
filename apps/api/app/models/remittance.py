from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.household import Household
    from app.models.membership import HouseholdMember


class Remittance(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "remittances"
    __table_args__ = (
        CheckConstraint("amount_php > 0", name="amount_php_positive"),
        CheckConstraint("source_amount > 0", name="source_amount_positive"),
        CheckConstraint("fee_php >= 0", name="fee_php_non_negative"),
        CheckConstraint("rate_used > 0", name="rate_used_positive"),
        CheckConstraint("length(source_currency) = 3", name="source_currency_iso_4217"),
        CheckConstraint("length(provider) > 0", name="provider_not_empty"),
        Index("ix_remittances_household_id_sent_at", "household_id", "sent_at"),
        Index("ix_remittances_recorded_by_member_id", "recorded_by_member_id"),
        Index("ix_remittances_provider", "provider"),
    )

    household_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
    )
    recorded_by_member_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("household_members.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount_php: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    source_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    source_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    fee_php: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0, server_default="0"
    )
    rate_used: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    household: Mapped[Household] = relationship(back_populates="remittances")
    recorded_by_member: Mapped[HouseholdMember | None] = relationship(back_populates="remittances")

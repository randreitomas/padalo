from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.household import Household
    from app.models.membership import HouseholdMember


class ForecastHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "forecast_history"
    __table_args__ = (
        CheckConstraint("amount_php > 0", name="amount_php_positive"),
        CheckConstraint("expected_savings_php >= 0", name="expected_savings_php_non_negative"),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1", name="confidence_between_zero_and_one"
        ),
        CheckConstraint("length(provider) > 0", name="provider_not_empty"),
        CheckConstraint("length(model_version) > 0", name="model_version_not_empty"),
        Index("ix_forecast_history_household_id_generated_at", "household_id", "generated_at"),
        Index("ix_forecast_history_requested_by_member_id", "requested_by_member_id"),
        Index("ix_forecast_history_provider", "provider"),
    )

    household_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
    )
    requested_by_member_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("household_members.id", ondelete="SET NULL"),
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    amount_php: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    recommended_send_date: Mapped[date] = mapped_column(Date, nullable=False)
    recommended_day: Mapped[str] = mapped_column(String(16), nullable=False)
    expected_savings_php: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    baseline_strategy: Mapped[str] = mapped_column(String(120), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    household: Mapped[Household] = relationship(back_populates="forecast_history")
    requested_by_member: Mapped[HouseholdMember | None] = relationship(
        back_populates="forecast_requests",
    )

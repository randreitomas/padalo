from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.household import Household
    from app.models.transaction import Transaction


class Envelope(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "envelopes"
    __table_args__ = (
        CheckConstraint("length(name) > 0", name="name_not_empty"),
        CheckConstraint("target_amount_php >= 0", name="target_amount_php_non_negative"),
        CheckConstraint("current_balance_php >= 0", name="current_balance_php_non_negative"),
        Index("ix_envelopes_household_id", "household_id"),
        Index("ix_envelopes_household_id_sort_order", "household_id", "sort_order"),
        Index(
            "uq_envelopes_household_id_name_active",
            "household_id",
            "name",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    household_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount_php: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        server_default="0",
    )
    current_balance_php: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        server_default="0",
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    household: Mapped[Household] = relationship(back_populates="envelopes")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="envelope")

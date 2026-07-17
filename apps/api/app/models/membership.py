from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.forecast import ForecastHistory
    from app.models.household import Household
    from app.models.remittance import Remittance
    from app.models.role import Role
    from app.models.transaction import Transaction
    from app.models.user import User


class HouseholdMember(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "household_members"
    __table_args__ = (
        CheckConstraint(
            "status IN ('invited', 'active', 'removed')",
            name="status_valid",
        ),
        Index("ix_household_members_household_id", "household_id"),
        Index("ix_household_members_user_id", "user_id"),
        Index("ix_household_members_role_id", "role_id"),
        Index("ix_household_members_status", "status"),
        Index(
            "uq_household_members_household_id_user_id_active",
            "household_id",
            "user_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    household_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    invited_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, default="active", server_default="active"
    )
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    household: Mapped[Household] = relationship(back_populates="members")
    user: Mapped[User] = relationship(
        back_populates="memberships",
        foreign_keys=[user_id],
    )
    invited_by: Mapped[User | None] = relationship(foreign_keys=[invited_by_user_id])
    role: Mapped[Role] = relationship(back_populates="memberships")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="logged_by_member")
    remittances: Mapped[list[Remittance]] = relationship(back_populates="recorded_by_member")
    forecast_requests: Mapped[list[ForecastHistory]] = relationship(
        back_populates="requested_by_member"
    )

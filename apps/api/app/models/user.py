from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.household import Household
    from app.models.membership import HouseholdMember


class User(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(auth_provider) > 0", name="auth_provider_not_empty"),
        CheckConstraint("length(auth_subject) > 0", name="auth_subject_not_empty"),
        Index("ix_users_auth_provider_auth_subject", "auth_provider", "auth_subject"),
        Index("uq_users_auth_provider_auth_subject", "auth_provider", "auth_subject", unique=True),
        Index(
            "uq_users_email_active",
            "email",
            unique=True,
            postgresql_where=text("email IS NOT NULL AND deleted_at IS NULL"),
        ),
    )

    auth_provider: Mapped[str] = mapped_column(String(32), nullable=False)
    auth_subject: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    locale: Mapped[str] = mapped_column(
        String(16), nullable=False, default="en-PH", server_default="en-PH"
    )
    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="Asia/Manila",
        server_default="Asia/Manila",
    )

    created_households: Mapped[list[Household]] = relationship(
        back_populates="created_by",
        foreign_keys="Household.created_by_user_id",
    )
    memberships: Mapped[list[HouseholdMember]] = relationship(
        back_populates="user",
        foreign_keys="HouseholdMember.user_id",
    )

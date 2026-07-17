from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.membership import HouseholdMember


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint("length(key) > 0", name="key_not_empty"),
        CheckConstraint("length(name) > 0", name="name_not_empty"),
        Index("uq_roles_key", "key", unique=True),
    )

    key: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    memberships: Mapped[list[HouseholdMember]] = relationship(back_populates="role")

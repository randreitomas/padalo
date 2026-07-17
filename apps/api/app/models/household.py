from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.bill import Bill
    from app.models.envelope import Envelope
    from app.models.forecast import ForecastHistory
    from app.models.membership import HouseholdMember
    from app.models.remittance import Remittance
    from app.models.transaction import Transaction
    from app.models.user import User


class Household(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "households"
    __table_args__ = (
        CheckConstraint("length(name) > 0", name="name_not_empty"),
        CheckConstraint("length(base_currency) = 3", name="base_currency_iso_4217"),
        CheckConstraint("length(home_country) = 2", name="home_country_iso_3166_alpha_2"),
        Index("ix_households_created_by_user_id", "created_by_user_id"),
    )

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    base_currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="PHP", server_default="PHP"
    )
    home_country: Mapped[str] = mapped_column(
        String(2), nullable=False, default="PH", server_default="PH"
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by: Mapped[User | None] = relationship(
        back_populates="created_households",
        foreign_keys=[created_by_user_id],
    )
    members: Mapped[list[HouseholdMember]] = relationship(back_populates="household")
    envelopes: Mapped[list[Envelope]] = relationship(back_populates="household")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="household")
    remittances: Mapped[list[Remittance]] = relationship(back_populates="household")
    bills: Mapped[list[Bill]] = relationship(back_populates="household")
    forecast_history: Mapped[list[ForecastHistory]] = relationship(back_populates="household")

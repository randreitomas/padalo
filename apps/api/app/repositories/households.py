from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.household import Household


class HouseholdRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(self, *, limit: int, offset: int) -> list[Household]:
        statement = (
            select(Household)
            .where(Household.deleted_at.is_(None))
            .order_by(Household.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(statement))

    def get_active(self, household_id: uuid.UUID) -> Household | None:
        statement = select(Household).where(
            Household.id == household_id,
            Household.deleted_at.is_(None),
        )
        return self.session.scalar(statement)

    def add(self, household: Household) -> Household:
        self.session.add(household)
        return household

    def soft_delete(self, household: Household) -> None:
        household.deleted_at = datetime.now(UTC)

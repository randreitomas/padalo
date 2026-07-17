from __future__ import annotations

import uuid

from app.api.exceptions import NotFoundError
from app.models.household import Household
from app.repositories.households import HouseholdRepository
from app.schemas.households import HouseholdCreate, HouseholdUpdate
from app.services.common import ServiceBase


class HouseholdService(ServiceBase):
    def __init__(self, session, households: HouseholdRepository) -> None:
        super().__init__(session)
        self.households = households

    def list(self, *, limit: int, offset: int) -> list[Household]:
        return self.households.list_active(limit=limit, offset=offset)

    def get(self, household_id: uuid.UUID) -> Household:
        household = self.households.get_active(household_id)
        if household is None:
            raise NotFoundError("Household not found.")
        return household

    def create(self, payload: HouseholdCreate) -> Household:
        household = self.households.add(Household(**payload.model_dump()))
        self.commit()
        self.session.refresh(household)
        return household

    def update(self, household_id: uuid.UUID, payload: HouseholdUpdate) -> Household:
        household = self.get(household_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(household, field, value)
        self.commit()
        self.session.refresh(household)
        return household

    def delete(self, household_id: uuid.UUID) -> None:
        household = self.get(household_id)
        self.households.soft_delete(household)
        self.commit()

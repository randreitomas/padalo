from __future__ import annotations

import uuid
from typing import Annotated

from pydantic import Field, StringConstraints, field_validator, model_validator

from app.schemas.common import APIModel, TimestampedRead

HouseholdName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)
]


class HouseholdCreate(APIModel):
    name: HouseholdName
    base_currency: str = Field(default="PHP", min_length=3, max_length=3)
    home_country: str = Field(default="PH", min_length=2, max_length=2)

    @field_validator("base_currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        value = value.upper()
        if not value.isalpha():
            raise ValueError("base_currency must contain three letters.")
        return value

    @field_validator("home_country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        value = value.upper()
        if not value.isalpha():
            raise ValueError("home_country must contain two letters.")
        return value


class HouseholdUpdate(APIModel):
    name: HouseholdName | None = None
    base_currency: str | None = Field(default=None, min_length=3, max_length=3)
    home_country: str | None = Field(default=None, min_length=2, max_length=2)

    @field_validator("base_currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return HouseholdCreate.normalize_currency(value) if value is not None else value

    @field_validator("home_country")
    @classmethod
    def normalize_country(cls, value: str | None) -> str | None:
        return HouseholdCreate.normalize_country(value) if value is not None else value

    @model_validator(mode="after")
    def require_change(self) -> HouseholdUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class HouseholdRead(TimestampedRead):
    id: uuid.UUID
    name: str
    base_currency: str
    home_country: str
    created_by_user_id: uuid.UUID | None

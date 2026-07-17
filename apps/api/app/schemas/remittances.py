from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints, field_validator, model_validator

from app.schemas.common import APIModel, TimestampedRead

PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
NonNegativeMoney = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
ProviderName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]


class RemittanceCreate(APIModel):
    recorded_by_member_id: uuid.UUID | None = None
    amount_php: PositiveMoney
    source_amount: PositiveMoney
    source_currency: str = Field(min_length=3, max_length=3)
    provider: ProviderName
    fee_php: NonNegativeMoney = Decimal("0.00")
    rate_used: Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=8)]
    sent_at: datetime

    @field_validator("source_currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        value = value.upper()
        if not value.isalpha():
            raise ValueError("source_currency must contain three letters.")
        return value


class RemittanceUpdate(APIModel):
    recorded_by_member_id: uuid.UUID | None = None
    amount_php: PositiveMoney | None = None
    source_amount: PositiveMoney | None = None
    source_currency: str | None = Field(default=None, min_length=3, max_length=3)
    provider: ProviderName | None = None
    fee_php: NonNegativeMoney | None = None
    rate_used: Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=8)] | None = None
    sent_at: datetime | None = None

    @field_validator("source_currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return RemittanceCreate.normalize_currency(value) if value is not None else value

    @model_validator(mode="after")
    def require_change(self) -> RemittanceUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class RemittanceRead(TimestampedRead):
    id: uuid.UUID
    household_id: uuid.UUID
    recorded_by_member_id: uuid.UUID | None
    amount_php: Decimal
    source_amount: Decimal
    source_currency: str
    provider: str
    fee_php: Decimal
    rate_used: Decimal
    sent_at: datetime

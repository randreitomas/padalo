from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from app.schemas.common import APIModel, TimestampedRead

EnvelopeName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]
NonNegativeMoney = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]


class EnvelopeCreate(APIModel):
    name: EnvelopeName
    target_amount_php: NonNegativeMoney = Decimal("0.00")
    current_balance_php: NonNegativeMoney = Decimal("0.00")
    sort_order: int = Field(default=0, ge=0, le=2_147_483_647)


class EnvelopeUpdate(APIModel):
    name: EnvelopeName | None = None
    target_amount_php: NonNegativeMoney | None = None
    current_balance_php: NonNegativeMoney | None = None
    sort_order: int | None = Field(default=None, ge=0, le=2_147_483_647)

    @model_validator(mode="after")
    def require_change(self) -> EnvelopeUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class EnvelopeRead(TimestampedRead):
    id: uuid.UUID
    household_id: uuid.UUID
    name: str
    target_amount_php: Decimal
    current_balance_php: Decimal
    sort_order: int

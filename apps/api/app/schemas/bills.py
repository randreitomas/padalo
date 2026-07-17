from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from app.schemas.common import APIModel, TimestampedRead

BillName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
Category = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
RecurrenceRule = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)
]
PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]


class BillStatus(str, Enum):
    scheduled = "scheduled"
    paid = "paid"
    skipped = "skipped"


class BillCreate(APIModel):
    name: BillName
    amount_php: PositiveMoney
    due_date: date
    category: Category | None = None
    recurring: bool = False
    recurrence_rule: RecurrenceRule | None = None
    status: BillStatus = BillStatus.scheduled

    @model_validator(mode="after")
    def validate_recurrence(self) -> BillCreate:
        if self.recurring and self.recurrence_rule is None:
            raise ValueError("recurrence_rule is required when recurring is true.")
        if not self.recurring and self.recurrence_rule is not None:
            raise ValueError("recurrence_rule must be omitted when recurring is false.")
        return self


class BillUpdate(APIModel):
    name: BillName | None = None
    amount_php: PositiveMoney | None = None
    due_date: date | None = None
    category: Category | None = None
    recurring: bool | None = None
    recurrence_rule: RecurrenceRule | None = None
    status: BillStatus | None = None

    @model_validator(mode="after")
    def require_change(self) -> BillUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class BillRead(TimestampedRead):
    id: uuid.UUID
    household_id: uuid.UUID
    name: str
    amount_php: Decimal
    due_date: date
    category: str | None
    recurring: bool
    recurrence_rule: str | None
    status: BillStatus

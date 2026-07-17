from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import Field, HttpUrl, StringConstraints, model_validator

from app.schemas.common import APIModel, TimestampedRead

PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
OptionalShortText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)
]
Note = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10_000)
]


class TransactionType(str, Enum):
    expense = "expense"
    refund = "refund"
    adjustment = "adjustment"


class TransactionSource(str, Enum):
    manual = "manual"
    chat = "chat"
    receipt = "receipt"


class TransactionCreate(APIModel):
    envelope_id: uuid.UUID | None = None
    logged_by_member_id: uuid.UUID | None = None
    amount_php: PositiveMoney
    transaction_type: TransactionType = TransactionType.expense
    source: TransactionSource = TransactionSource.manual
    merchant: OptionalShortText | None = None
    note: Note | None = None
    receipt_url: HttpUrl | None = None
    occurred_on: date


class TransactionUpdate(APIModel):
    envelope_id: uuid.UUID | None = None
    logged_by_member_id: uuid.UUID | None = None
    amount_php: PositiveMoney | None = None
    transaction_type: TransactionType | None = None
    source: TransactionSource | None = None
    merchant: OptionalShortText | None = None
    note: Note | None = None
    receipt_url: HttpUrl | None = None
    occurred_on: date | None = None

    @model_validator(mode="after")
    def require_change(self) -> TransactionUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class TransactionRead(TimestampedRead):
    id: uuid.UUID
    household_id: uuid.UUID
    envelope_id: uuid.UUID | None
    logged_by_member_id: uuid.UUID | None
    amount_php: Decimal
    transaction_type: TransactionType
    source: TransactionSource
    merchant: str | None
    note: str | None
    receipt_url: str | None
    occurred_on: date

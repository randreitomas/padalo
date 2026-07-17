from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class AgentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


ShortText = Annotated[str, StringConstraints(min_length=1, max_length=160)]
LongText = Annotated[str, StringConstraints(min_length=1, max_length=2_000)]
ChatText = Annotated[str, StringConstraints(min_length=1, max_length=2_000)]
PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
NonNegativeMoney = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
PositiveRate = Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=8)]


class AgentChatRequest(AgentModel):
    message: ChatText
    conversation_id: uuid.UUID | None = None


class AgentMemoryMessage(AgentModel):
    role: Literal["user", "assistant"]
    content: ChatText


class GetBudgetStatusInput(AgentModel):
    envelope: ShortText


class BudgetStatusOutput(AgentModel):
    envelope: str
    allocated_php: Decimal
    available_php: Decimal
    spent_estimate_php: Decimal
    status: Literal["healthy", "warning_low", "empty"]


class LogExpenseInput(AgentModel):
    amount_php: PositiveMoney
    category: ShortText
    merchant: ShortText | None
    note: LongText | None
    occurred_on: date


class ExpenseLoggedOutput(AgentModel):
    transaction_id: uuid.UUID
    envelope: str
    amount_php: Decimal
    remaining_envelope_balance_php: Decimal
    occurred_on: date


class UpcomingBillsInput(AgentModel):
    timeframe_days: Annotated[int, Field(ge=1, le=90)]


class UpcomingBill(AgentModel):
    name: str
    amount_php: Decimal
    due_date: date
    category: str | None


class UpcomingBillsOutput(AgentModel):
    timeframe_days: int
    bills: list[UpcomingBill]
    total_due_php: Decimal


class CreateRemittanceInput(AgentModel):
    amount_php: PositiveMoney
    source_amount: PositiveMoney
    source_currency: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    provider: ShortText
    fee_php: NonNegativeMoney
    rate_used: PositiveRate
    sent_at: datetime


class RemittanceCreatedOutput(AgentModel):
    remittance_id: uuid.UUID
    amount_php: Decimal
    provider: str
    sent_at: datetime


class SearchTransactionsInput(AgentModel):
    query: ShortText
    days: Annotated[int, Field(ge=1, le=365)]


class TransactionSearchMatch(AgentModel):
    transaction_id: uuid.UUID
    amount_php: Decimal
    merchant: str | None
    note: str | None
    envelope: str | None
    occurred_on: date


class SearchTransactionsOutput(AgentModel):
    query: str
    days: int
    matches: list[TransactionSearchMatch]


class ForecastRemittanceInput(AgentModel):
    amount_php: PositiveMoney | None
    provider: ShortText | None


class ForecastRecommendation(AgentModel):
    recommended_day: str
    expected_savings_php: Decimal
    confidence: str
    provider: str
    amount_php: Decimal
    is_mock: bool
    disclaimer: str


class AgentFinalResponse(AgentModel):
    message: ChatText
    recommendation: ForecastRecommendation | None
    records_changed: list[Literal["transaction", "remittance"]]


class ToolErrorPayload(AgentModel):
    code: str
    message: str


class ToolExecution(AgentModel):
    call_id: str
    name: str
    ok: bool
    data: dict[str, Any] | None
    error: ToolErrorPayload | None


class AgentStreamEvent(AgentModel):
    event: str
    data: dict[str, Any]

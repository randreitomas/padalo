from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from padalo_agent.schemas.json_schema import strict_json_schema
from padalo_agent.schemas.models import (
    CreateRemittanceInput,
    ForecastRemittanceInput,
    GetBudgetStatusInput,
    LogExpenseInput,
    SearchTransactionsInput,
    UpcomingBillsInput,
)

_TOOL_SPECS: tuple[tuple[str, str, type[BaseModel]], ...] = (
    (
        "get_budget_status",
        "Read the allocation and available balance for one household envelope.",
        GetBudgetStatusInput,
    ),
    (
        "log_expense",
        "Record a clearly requested household expense against an existing envelope.",
        LogExpenseInput,
    ),
    (
        "upcoming_bills",
        "Read scheduled household bills due in the requested number of days.",
        UpcomingBillsInput,
    ),
    (
        "create_remittance",
        "Record a clearly requested remittance ledger entry. This never moves money.",
        CreateRemittanceInput,
    ),
    (
        "search_transactions",
        "Search recent household transactions by merchant, note, or envelope name.",
        SearchTransactionsInput,
    ),
    (
        "forecast_remittance",
        "Return a temporary FXPilot demo timing estimate. It is not a live provider quote.",
        ForecastRemittanceInput,
    ),
)

INPUT_MODELS = {name: model for name, _, model in _TOOL_SPECS}


def tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "name": name,
            "description": description,
            "parameters": strict_json_schema(model),
            "strict": True,
        }
        for name, description, model in _TOOL_SPECS
    ]

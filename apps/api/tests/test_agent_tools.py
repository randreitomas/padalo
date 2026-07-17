import json
import uuid
from datetime import date
from decimal import Decimal

from padalo_agent.schemas import (
    BudgetStatusOutput,
    CreateRemittanceInput,
    ExpenseLoggedOutput,
    GetBudgetStatusInput,
    LogExpenseInput,
    RemittanceCreatedOutput,
    SearchTransactionsInput,
    SearchTransactionsOutput,
    TransactionSearchMatch,
    UpcomingBillsInput,
    UpcomingBillsOutput,
)
from padalo_agent.tools.definitions import tool_definitions
from padalo_agent.tools.router import ToolRouter


class FakeGateway:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get_budget_status(self, payload: GetBudgetStatusInput) -> BudgetStatusOutput:
        self.calls.append("get_budget_status")
        return BudgetStatusOutput(
            envelope=payload.envelope,
            allocated_php=Decimal("6000.00"),
            available_php=Decimal("4500.00"),
            spent_estimate_php=Decimal("1500.00"),
            status="healthy",
        )

    def log_expense(self, payload: LogExpenseInput) -> ExpenseLoggedOutput:
        self.calls.append("log_expense")
        return ExpenseLoggedOutput(
            transaction_id=uuid.UUID("11111111-1111-4111-8111-111111111111"),
            envelope=payload.category,
            amount_php=payload.amount_php,
            remaining_envelope_balance_php=Decimal("4350.00"),
            occurred_on=payload.occurred_on,
        )

    def upcoming_bills(self, payload: UpcomingBillsInput) -> UpcomingBillsOutput:
        self.calls.append("upcoming_bills")
        return UpcomingBillsOutput(
            timeframe_days=payload.timeframe_days,
            bills=[],
            total_due_php=Decimal("0.00"),
        )

    def create_remittance(self, payload: CreateRemittanceInput) -> RemittanceCreatedOutput:
        self.calls.append("create_remittance")
        return RemittanceCreatedOutput(
            remittance_id=uuid.UUID("22222222-2222-4222-8222-222222222222"),
            amount_php=payload.amount_php,
            provider=payload.provider,
            sent_at=payload.sent_at,
        )

    def search_transactions(self, payload: SearchTransactionsInput) -> SearchTransactionsOutput:
        self.calls.append("search_transactions")
        return SearchTransactionsOutput(
            query=payload.query,
            days=payload.days,
            matches=[
                TransactionSearchMatch(
                    transaction_id=uuid.UUID("33333333-3333-4333-8333-333333333333"),
                    amount_php=Decimal("1500.00"),
                    merchant="SM Supermarket",
                    note="Weekend groceries",
                    envelope="Groceries",
                    occurred_on=date(2026, 7, 17),
                )
            ],
        )


def test_every_initial_tool_uses_typed_json_and_returns_a_structured_result() -> None:
    gateway = FakeGateway()
    router = ToolRouter(gateway)
    tool_arguments = {
        "get_budget_status": {"envelope": "Groceries"},
        "log_expense": {
            "amount_php": "150.00",
            "category": "Groceries",
            "merchant": "SM Supermarket",
            "note": "Fruit and vegetables",
            "occurred_on": "2026-07-17",
        },
        "upcoming_bills": {"timeframe_days": 14},
        "create_remittance": {
            "amount_php": "15000.00",
            "source_amount": "260.00",
            "source_currency": "SGD",
            "provider": "Wise",
            "fee_php": "110.00",
            "rate_used": "57.69230769",
            "sent_at": "2026-07-17T09:30:00+00:00",
        },
        "search_transactions": {"query": "supermarket", "days": 30},
        "forecast_remittance": {"amount_php": "15000.00", "provider": "Wise"},
    }

    results = {
        name: router.execute(
            name=name,
            arguments_json=json.dumps(arguments),
            call_id=f"call-{index}",
        )
        for index, (name, arguments) in enumerate(tool_arguments.items(), start=1)
    }

    assert all(result.ok for result in results.values())
    assert results["get_budget_status"].data["available_php"] == "4500.00"
    assert results["log_expense"].data["remaining_envelope_balance_php"] == "4350.00"
    assert results["upcoming_bills"].data["total_due_php"] == "0.00"
    assert results["create_remittance"].data["provider"] == "Wise"
    assert results["search_transactions"].data["matches"][0]["merchant"] == "SM Supermarket"
    assert results["forecast_remittance"].data["recommended_day"] == "Thursday"
    assert results["forecast_remittance"].data["is_mock"] is True
    assert gateway.calls == [
        "get_budget_status",
        "log_expense",
        "upcoming_bills",
        "create_remittance",
        "search_transactions",
    ]


def test_mock_forecast_accepts_explicit_demo_assumptions() -> None:
    result = ToolRouter(FakeGateway()).execute(
        name="forecast_remittance",
        arguments_json='{"amount_php": null, "provider": null}',
        call_id="forecast-with-assumptions",
    )

    assert result.ok is True
    assert result.data["provider"] == "Demo provider"
    assert result.data["amount_php"] == "15000.00"


def test_invalid_or_duplicate_tool_calls_stay_safe_and_structured() -> None:
    router = ToolRouter(FakeGateway())

    invalid = router.execute(
        name="log_expense",
        arguments_json='{"amount_php": -1}',
        call_id="invalid-call",
    )
    duplicate = router.execute(
        name="log_expense",
        arguments_json='{"amount_php": -1}',
        call_id="invalid-call",
    )

    assert invalid.ok is False
    assert invalid.error.code == "invalid_arguments"
    assert duplicate.ok is False
    assert duplicate.error.code == "duplicate_call"


def test_tool_definitions_require_strict_object_schemas() -> None:
    definitions = tool_definitions()

    assert {definition["name"] for definition in definitions} == {
        "create_remittance",
        "forecast_remittance",
        "get_budget_status",
        "log_expense",
        "search_transactions",
        "upcoming_bills",
    }
    for definition in definitions:
        schema = definition["parameters"]
        assert definition["strict"] is True
        assert schema["additionalProperties"] is False
        assert set(schema["required"]) == set(schema["properties"])

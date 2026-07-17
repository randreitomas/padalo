from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ValidationError

from padalo_agent.schemas.models import (
    BudgetStatusOutput,
    CreateRemittanceInput,
    ExpenseLoggedOutput,
    GetBudgetStatusInput,
    LogExpenseInput,
    RemittanceCreatedOutput,
    SearchTransactionsInput,
    SearchTransactionsOutput,
    ToolErrorPayload,
    ToolExecution,
    UpcomingBillsInput,
    UpcomingBillsOutput,
)
from padalo_agent.tools.definitions import INPUT_MODELS
from padalo_agent.tools.mock_forecast import forecast_remittance


class AgentToolError(Exception):
    """A safe, user-facing error raised by the application service adapter."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class ToolGateway(Protocol):
    def get_budget_status(self, payload: GetBudgetStatusInput) -> BudgetStatusOutput: ...

    def log_expense(self, payload: LogExpenseInput) -> ExpenseLoggedOutput: ...

    def upcoming_bills(self, payload: UpcomingBillsInput) -> UpcomingBillsOutput: ...

    def create_remittance(self, payload: CreateRemittanceInput) -> RemittanceCreatedOutput: ...

    def search_transactions(self, payload: SearchTransactionsInput) -> SearchTransactionsOutput: ...


class ToolRouter:
    """Validates model function calls before they reach typed application callbacks."""

    def __init__(self, gateway: ToolGateway) -> None:
        self.gateway = gateway
        self._executed_call_ids: set[str] = set()

    def execute(self, *, name: str, arguments_json: str, call_id: str) -> ToolExecution:
        if call_id in self._executed_call_ids:
            return self._error(
                call_id,
                name,
                "duplicate_call",
                "This action has already been handled for the current conversation turn.",
            )
        self._executed_call_ids.add(call_id)

        input_model = INPUT_MODELS.get(name)
        if input_model is None:
            return self._error(
                call_id,
                name,
                "unknown_tool",
                "That household action is not available.",
            )

        try:
            payload = input_model.model_validate_json(arguments_json)
        except ValidationError:
            return self._error(
                call_id,
                name,
                "invalid_arguments",
                "The details for this action were incomplete or invalid.",
            )

        try:
            result = self._dispatch(name, payload)
        except AgentToolError as error:
            return self._error(call_id, name, error.code, error.message)
        except Exception:
            return self._error(
                call_id,
                name,
                "tool_unavailable",
                "This household action could not be completed right now.",
            )

        return ToolExecution(
            call_id=call_id,
            name=name,
            ok=True,
            data=result.model_dump(mode="json"),
            error=None,
        )

    def _dispatch(self, name: str, payload: BaseModel) -> BaseModel:
        if name == "forecast_remittance":
            return forecast_remittance(payload)  # type: ignore[arg-type]
        return getattr(self.gateway, name)(payload)

    @staticmethod
    def _error(call_id: str, name: str, code: str, message: str) -> ToolExecution:
        return ToolExecution(
            call_id=call_id,
            name=name,
            ok=False,
            data=None,
            error=ToolErrorPayload(code=code, message=message),
        )

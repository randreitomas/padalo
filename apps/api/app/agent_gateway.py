from __future__ import annotations

import uuid
from datetime import date, timedelta
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
    UpcomingBill,
    UpcomingBillsInput,
    UpcomingBillsOutput,
)
from padalo_agent.tools.router import AgentToolError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_bill_service,
    get_envelope_service,
    get_household_service,
    get_remittance_service,
    get_transaction_service,
)
from app.api.exceptions import DomainError, LedgerInvariantError, NotFoundError
from app.schemas.remittances import RemittanceCreate
from app.schemas.transactions import TransactionCreate, TransactionSource, TransactionType
from app.services.households import HouseholdService
from app.services.ledger import BillService, EnvelopeService, RemittanceService, TransactionService


class LedgerToolGateway:
    """Application adapter exposed to the agent as typed callbacks, never a database handle."""

    def __init__(
        self,
        *,
        household_id: uuid.UUID,
        households: HouseholdService,
        envelopes: EnvelopeService,
        transactions: TransactionService,
        remittances: RemittanceService,
        bills: BillService,
    ) -> None:
        self.household_id = household_id
        self.households = households
        self.envelopes = envelopes
        self.transactions = transactions
        self.remittances = remittances
        self.bills = bills

    def verify_household(self) -> None:
        try:
            self.households.get(self.household_id)
        except DomainError as error:
            self._raise_tool_error(error)

    def get_budget_status(self, payload: GetBudgetStatusInput) -> BudgetStatusOutput:
        envelope = self._find_envelope(payload.envelope)
        allocated = envelope.target_amount_php
        available = envelope.current_balance_php
        spent_estimate = max(allocated - available, Decimal("0.00"))
        if available == 0:
            status = "empty"
        elif allocated > 0 and available <= allocated * Decimal("0.20"):
            status = "warning_low"
        else:
            status = "healthy"

        return BudgetStatusOutput(
            envelope=envelope.name,
            allocated_php=allocated,
            available_php=available,
            spent_estimate_php=spent_estimate,
            status=status,
        )

    def log_expense(self, payload: LogExpenseInput) -> ExpenseLoggedOutput:
        envelope = self._find_envelope(payload.category)
        try:
            transaction = self.transactions.create(
                self.household_id,
                TransactionCreate(
                    envelope_id=envelope.id,
                    amount_php=payload.amount_php,
                    transaction_type=TransactionType.expense,
                    source=TransactionSource.chat,
                    merchant=payload.merchant,
                    note=payload.note,
                    occurred_on=payload.occurred_on,
                ),
            )
            updated_envelope = self.envelopes.get(self.household_id, envelope.id)
        except DomainError as error:
            self._raise_tool_error(error)

        return ExpenseLoggedOutput(
            transaction_id=transaction.id,
            envelope=updated_envelope.name,
            amount_php=transaction.amount_php,
            remaining_envelope_balance_php=updated_envelope.current_balance_php,
            occurred_on=transaction.occurred_on,
        )

    def upcoming_bills(self, payload: UpcomingBillsInput) -> UpcomingBillsOutput:
        today = date.today()
        try:
            bills = self.bills.list(
                self.household_id,
                limit=100,
                offset=0,
                status="scheduled",
                due_from=today,
                due_to=today + timedelta(days=payload.timeframe_days),
            )
        except DomainError as error:
            self._raise_tool_error(error)

        return UpcomingBillsOutput(
            timeframe_days=payload.timeframe_days,
            bills=[
                UpcomingBill(
                    name=bill.name,
                    amount_php=bill.amount_php,
                    due_date=bill.due_date,
                    category=bill.category,
                )
                for bill in bills
            ],
            total_due_php=sum((bill.amount_php for bill in bills), Decimal("0.00")),
        )

    def create_remittance(self, payload: CreateRemittanceInput) -> RemittanceCreatedOutput:
        try:
            remittance = self.remittances.create(
                self.household_id,
                RemittanceCreate(
                    amount_php=payload.amount_php,
                    source_amount=payload.source_amount,
                    source_currency=payload.source_currency,
                    provider=payload.provider,
                    fee_php=payload.fee_php,
                    rate_used=payload.rate_used,
                    sent_at=payload.sent_at,
                ),
            )
        except DomainError as error:
            self._raise_tool_error(error)

        return RemittanceCreatedOutput(
            remittance_id=remittance.id,
            amount_php=remittance.amount_php,
            provider=remittance.provider,
            sent_at=remittance.sent_at,
        )

    def search_transactions(self, payload: SearchTransactionsInput) -> SearchTransactionsOutput:
        today = date.today()
        try:
            transactions = self.transactions.list(
                self.household_id,
                limit=100,
                offset=0,
                envelope_id=None,
                start_date=today - timedelta(days=payload.days),
                end_date=today,
            )
            envelope_names = {
                envelope.id: envelope.name
                for envelope in self.envelopes.list(self.household_id, limit=100, offset=0)
            }
        except DomainError as error:
            self._raise_tool_error(error)

        query = payload.query.casefold()
        matches = []
        for transaction in transactions:
            envelope_name = envelope_names.get(transaction.envelope_id)
            searchable = " ".join(
                value
                for value in (transaction.merchant, transaction.note, envelope_name)
                if value is not None
            ).casefold()
            if query in searchable:
                matches.append(
                    TransactionSearchMatch(
                        transaction_id=transaction.id,
                        amount_php=transaction.amount_php,
                        merchant=transaction.merchant,
                        note=transaction.note,
                        envelope=envelope_name,
                        occurred_on=transaction.occurred_on,
                    )
                )
            if len(matches) == 20:
                break

        return SearchTransactionsOutput(query=payload.query, days=payload.days, matches=matches)

    def _find_envelope(self, category: str):
        try:
            envelopes = self.envelopes.list(self.household_id, limit=100, offset=0)
        except DomainError as error:
            self._raise_tool_error(error)

        normalized = category.casefold()
        for envelope in envelopes:
            if envelope.name.casefold() == normalized:
                return envelope
        raise AgentToolError(
            "envelope_not_found",
            f"I could not find an active '{category}' envelope in this household.",
        )

    @staticmethod
    def _raise_tool_error(error: DomainError) -> None:
        if isinstance(error, NotFoundError):
            raise AgentToolError("not_found", error.detail) from error
        if isinstance(error, LedgerInvariantError):
            raise AgentToolError("ledger_constraint", error.detail) from error
        raise AgentToolError("ledger_error", error.detail) from error


def create_ledger_tool_gateway(session: Session, household_id: uuid.UUID) -> LedgerToolGateway:
    return LedgerToolGateway(
        household_id=household_id,
        households=get_household_service(session),
        envelopes=get_envelope_service(session),
        transactions=get_transaction_service(session),
        remittances=get_remittance_service(session),
        bills=get_bill_service(session),
    )

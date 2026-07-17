import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.api.exceptions import LedgerInvariantError
from app.models.envelope import Envelope
from app.models.household import Household
from app.models.transaction import Transaction
from app.schemas.transactions import TransactionCreate, TransactionType, TransactionUpdate
from app.services.ledger import TransactionService


class FakeSession:
    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1

    def refresh(self, _: object) -> None:
        return None


class FakeHouseholds:
    def __init__(self, household: Household) -> None:
        self.household = household

    def get_active(self, household_id: uuid.UUID) -> Household | None:
        return self.household if household_id == self.household.id else None


class FakeEnvelopes:
    def __init__(self, envelope: Envelope) -> None:
        self.envelope = envelope

    def get_for_household(
        self, household_id: uuid.UUID, envelope_id: uuid.UUID, *, include_deleted: bool = False
    ) -> Envelope | None:
        if household_id == self.envelope.household_id and envelope_id == self.envelope.id:
            return self.envelope
        return None


class FakeMembers:
    def get_active_for_household(self, _: uuid.UUID, __: uuid.UUID) -> None:
        return None


class FakeTransactions:
    def __init__(self, transaction: Transaction | None = None) -> None:
        self.transaction = transaction
        self.added: Transaction | None = None
        self.deleted = False

    def get_for_household(
        self, household_id: uuid.UUID, transaction_id: uuid.UUID
    ) -> Transaction | None:
        if (
            self.transaction is not None
            and household_id == self.transaction.household_id
            and transaction_id == self.transaction.id
        ):
            return self.transaction
        return None

    def add(self, transaction: Transaction) -> Transaction:
        self.added = transaction
        return transaction

    def soft_delete(self, _: Transaction) -> None:
        self.deleted = True


def make_service(balance: Decimal, transaction: Transaction | None = None):
    household = Household(id=uuid.uuid4(), name="Santos", base_currency="PHP", home_country="PH")
    envelope = Envelope(
        id=uuid.uuid4(),
        household_id=household.id,
        name="Groceries",
        target_amount_php=Decimal("1000.00"),
        current_balance_php=balance,
        sort_order=0,
    )
    if transaction is not None:
        transaction.household_id = household.id
        transaction.envelope_id = envelope.id
    session = FakeSession()
    transactions = FakeTransactions(transaction)
    service = TransactionService(
        session,
        FakeHouseholds(household),  # type: ignore[arg-type]
        FakeEnvelopes(envelope),  # type: ignore[arg-type]
        FakeMembers(),  # type: ignore[arg-type]
        transactions,  # type: ignore[arg-type]
    )
    return service, household, envelope, session, transactions


def test_creating_expense_reduces_its_envelope_balance() -> None:
    service, household, envelope, session, transactions = make_service(Decimal("100.00"))

    created = service.create(
        household.id,
        TransactionCreate(
            envelope_id=envelope.id,
            amount_php=Decimal("25.00"),
            occurred_on=date(2026, 7, 17),
        ),
    )

    assert created is transactions.added
    assert envelope.current_balance_php == Decimal("75.00")
    assert session.commit_count == 1


def test_updating_transaction_reconciles_the_previous_balance_impact() -> None:
    transaction = Transaction(
        id=uuid.uuid4(),
        household_id=uuid.uuid4(),
        envelope_id=uuid.uuid4(),
        amount_php=Decimal("20.00"),
        transaction_type="expense",
        source="manual",
        occurred_on=date(2026, 7, 17),
    )
    service, household, envelope, _, _ = make_service(Decimal("80.00"), transaction)

    service.update(
        household.id,
        transaction.id,
        TransactionUpdate(amount_php=Decimal("30.00"), transaction_type=TransactionType.refund),
    )

    assert envelope.current_balance_php == Decimal("130.00")
    assert transaction.transaction_type == "refund"


def test_expense_that_would_overdraw_an_envelope_is_rejected() -> None:
    service, household, envelope, session, transactions = make_service(Decimal("10.00"))

    with pytest.raises(LedgerInvariantError):
        service.create(
            household.id,
            TransactionCreate(
                envelope_id=envelope.id,
                amount_php=Decimal("20.00"),
                occurred_on=date(2026, 7, 17),
            ),
        )

    assert envelope.current_balance_php == Decimal("10.00")
    assert transactions.added is None
    assert session.rollback_count == 1

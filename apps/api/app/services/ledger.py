from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum

from sqlalchemy.orm import Session

from app.api.exceptions import DomainValidationError, LedgerInvariantError, NotFoundError
from app.models.bill import Bill
from app.models.envelope import Envelope
from app.models.remittance import Remittance
from app.models.transaction import Transaction
from app.repositories.households import HouseholdRepository
from app.repositories.ledger import (
    BillRepository,
    EnvelopeRepository,
    HouseholdMemberRepository,
    RemittanceRepository,
    TransactionRepository,
)
from app.schemas.bills import BillCreate, BillUpdate
from app.schemas.envelopes import EnvelopeCreate, EnvelopeUpdate
from app.schemas.remittances import RemittanceCreate, RemittanceUpdate
from app.schemas.transactions import TransactionCreate, TransactionUpdate
from app.services.common import ServiceBase


class HouseholdScopedService(ServiceBase):
    def __init__(self, session: Session, households: HouseholdRepository) -> None:
        super().__init__(session)
        self.households = households

    def require_household(self, household_id: uuid.UUID):
        household = self.households.get_active(household_id)
        if household is None:
            raise NotFoundError("Household not found.")
        return household


class EnvelopeService(HouseholdScopedService):
    def __init__(
        self,
        session: Session,
        households: HouseholdRepository,
        envelopes: EnvelopeRepository,
    ) -> None:
        super().__init__(session, households)
        self.envelopes = envelopes

    def list(self, household_id: uuid.UUID, *, limit: int, offset: int) -> list[Envelope]:
        self.require_household(household_id)
        return self.envelopes.list_active(household_id, limit=limit, offset=offset)

    def get(self, household_id: uuid.UUID, envelope_id: uuid.UUID) -> Envelope:
        self.require_household(household_id)
        envelope = self.envelopes.get_for_household(household_id, envelope_id)
        if envelope is None:
            raise NotFoundError("Envelope not found.")
        return envelope

    def create(self, household_id: uuid.UUID, payload: EnvelopeCreate) -> Envelope:
        self.require_household(household_id)
        envelope = self.envelopes.add(Envelope(household_id=household_id, **payload.model_dump()))
        self.commit()
        self.session.refresh(envelope)
        return envelope

    def update(
        self, household_id: uuid.UUID, envelope_id: uuid.UUID, payload: EnvelopeUpdate
    ) -> Envelope:
        envelope = self.get(household_id, envelope_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(envelope, field, value)
        self.commit()
        self.session.refresh(envelope)
        return envelope

    def delete(self, household_id: uuid.UUID, envelope_id: uuid.UUID) -> None:
        envelope = self.get(household_id, envelope_id)
        self.envelopes.soft_delete(envelope)
        self.commit()


class TransactionService(HouseholdScopedService):
    def __init__(
        self,
        session: Session,
        households: HouseholdRepository,
        envelopes: EnvelopeRepository,
        members: HouseholdMemberRepository,
        transactions: TransactionRepository,
    ) -> None:
        super().__init__(session, households)
        self.envelopes = envelopes
        self.members = members
        self.transactions = transactions

    def list(
        self,
        household_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
        envelope_id: uuid.UUID | None,
        start_date: date | None,
        end_date: date | None,
    ) -> list[Transaction]:
        self.require_household(household_id)
        return self.transactions.list_active(
            household_id,
            limit=limit,
            offset=offset,
            envelope_id=envelope_id,
            start_date=start_date,
            end_date=end_date,
        )

    def get(self, household_id: uuid.UUID, transaction_id: uuid.UUID) -> Transaction:
        self.require_household(household_id)
        transaction = self.transactions.get_for_household(household_id, transaction_id)
        if transaction is None:
            raise NotFoundError("Transaction not found.")
        return transaction

    def create(self, household_id: uuid.UUID, payload: TransactionCreate) -> Transaction:
        self.require_household(household_id)
        envelope = self._validate_envelope(household_id, payload.envelope_id)
        self._validate_member(household_id, payload.logged_by_member_id)
        transaction = Transaction(
            household_id=household_id,
            envelope_id=payload.envelope_id,
            logged_by_member_id=payload.logged_by_member_id,
            amount_php=payload.amount_php,
            transaction_type=payload.transaction_type.value,
            source=payload.source.value,
            merchant=payload.merchant,
            note=payload.note,
            receipt_url=str(payload.receipt_url) if payload.receipt_url is not None else None,
            occurred_on=payload.occurred_on,
        )
        try:
            if envelope is not None:
                self._apply_balance_delta(
                    envelope,
                    self._balance_impact(transaction.transaction_type, transaction.amount_php),
                )
            self.transactions.add(transaction)
            self.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(transaction)
        return transaction

    def update(
        self, household_id: uuid.UUID, transaction_id: uuid.UUID, payload: TransactionUpdate
    ) -> Transaction:
        transaction = self.get(household_id, transaction_id)
        changes = payload.model_dump(exclude_unset=True)
        new_envelope_id = changes.get("envelope_id", transaction.envelope_id)
        new_member_id = changes.get("logged_by_member_id", transaction.logged_by_member_id)
        new_amount = changes.get("amount_php", transaction.amount_php)
        new_type = changes.get("transaction_type", transaction.transaction_type)
        new_type_value = new_type.value if isinstance(new_type, Enum) else new_type

        old_envelope = self._existing_envelope(household_id, transaction.envelope_id)
        new_envelope = (
            self._validate_envelope(household_id, new_envelope_id)
            if "envelope_id" in changes
            else old_envelope
        )
        if "logged_by_member_id" in changes:
            self._validate_member(household_id, new_member_id)

        try:
            old_impact = self._balance_impact(transaction.transaction_type, transaction.amount_php)
            new_impact = self._balance_impact(new_type_value, new_amount)
            if transaction.envelope_id == new_envelope_id:
                if old_envelope is not None:
                    self._apply_balance_delta(old_envelope, new_impact - old_impact)
            else:
                if old_envelope is not None:
                    self._apply_balance_delta(old_envelope, -old_impact)
                if new_envelope is not None:
                    self._apply_balance_delta(new_envelope, new_impact)

            for field, value in changes.items():
                if isinstance(value, Enum):
                    value = value.value
                elif field == "receipt_url" and value is not None:
                    value = str(value)
                setattr(transaction, field, value)
            self.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(transaction)
        return transaction

    def delete(self, household_id: uuid.UUID, transaction_id: uuid.UUID) -> None:
        transaction = self.get(household_id, transaction_id)
        envelope = self._existing_envelope(household_id, transaction.envelope_id)
        try:
            if envelope is not None:
                self._apply_balance_delta(
                    envelope,
                    -self._balance_impact(transaction.transaction_type, transaction.amount_php),
                )
            self.transactions.soft_delete(transaction)
            self.commit()
        except Exception:
            self.session.rollback()
            raise

    def _validate_envelope(
        self, household_id: uuid.UUID, envelope_id: uuid.UUID | None
    ) -> Envelope | None:
        if envelope_id is None:
            return None
        envelope = self.envelopes.get_for_household(household_id, envelope_id)
        if envelope is None:
            raise NotFoundError("Envelope not found in this household.")
        return envelope

    def _existing_envelope(
        self, household_id: uuid.UUID, envelope_id: uuid.UUID | None
    ) -> Envelope | None:
        if envelope_id is None:
            return None
        envelope = self.envelopes.get_for_household(
            household_id, envelope_id, include_deleted=True
        )
        if envelope is None:
            raise LedgerInvariantError("Transaction references an unavailable envelope.")
        return envelope

    def _validate_member(self, household_id: uuid.UUID, member_id: uuid.UUID | None) -> None:
        if member_id is None:
            return
        member = self.members.get_active_for_household(household_id, member_id)
        if member is None:
            raise NotFoundError("Active household member not found.")

    @staticmethod
    def _balance_impact(transaction_type: str, amount: Decimal) -> Decimal:
        # The frozen schema has only positive amounts; adjustments are debit corrections.
        return amount if transaction_type == "refund" else -amount

    @staticmethod
    def _apply_balance_delta(envelope: Envelope, delta: Decimal) -> None:
        next_balance = envelope.current_balance_php + delta
        if next_balance < 0:
            raise LedgerInvariantError("Transaction would make the envelope balance negative.")
        envelope.current_balance_php = next_balance


class RemittanceService(HouseholdScopedService):
    def __init__(
        self,
        session: Session,
        households: HouseholdRepository,
        members: HouseholdMemberRepository,
        remittances: RemittanceRepository,
    ) -> None:
        super().__init__(session, households)
        self.members = members
        self.remittances = remittances

    def list(
        self,
        household_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
        start_at: datetime | None,
        end_at: datetime | None,
    ) -> list[Remittance]:
        self.require_household(household_id)
        return self.remittances.list_active(
            household_id,
            limit=limit,
            offset=offset,
            start_at=start_at,
            end_at=end_at,
        )

    def get(self, household_id: uuid.UUID, remittance_id: uuid.UUID) -> Remittance:
        self.require_household(household_id)
        remittance = self.remittances.get_for_household(household_id, remittance_id)
        if remittance is None:
            raise NotFoundError("Remittance not found.")
        return remittance

    def create(self, household_id: uuid.UUID, payload: RemittanceCreate) -> Remittance:
        self.require_household(household_id)
        self._validate_member(household_id, payload.recorded_by_member_id)
        remittance = self.remittances.add(
            Remittance(household_id=household_id, **payload.model_dump())
        )
        self.commit()
        self.session.refresh(remittance)
        return remittance

    def update(
        self, household_id: uuid.UUID, remittance_id: uuid.UUID, payload: RemittanceUpdate
    ) -> Remittance:
        remittance = self.get(household_id, remittance_id)
        changes = payload.model_dump(exclude_unset=True)
        if "recorded_by_member_id" in changes:
            self._validate_member(household_id, changes["recorded_by_member_id"])
        for field, value in changes.items():
            setattr(remittance, field, value)
        self.commit()
        self.session.refresh(remittance)
        return remittance

    def delete(self, household_id: uuid.UUID, remittance_id: uuid.UUID) -> None:
        remittance = self.get(household_id, remittance_id)
        self.remittances.soft_delete(remittance)
        self.commit()

    def _validate_member(self, household_id: uuid.UUID, member_id: uuid.UUID | None) -> None:
        if (
            member_id is not None
            and self.members.get_active_for_household(household_id, member_id) is None
        ):
            raise NotFoundError("Active household member not found.")


class BillService(HouseholdScopedService):
    def __init__(
        self, session: Session, households: HouseholdRepository, bills: BillRepository
    ) -> None:
        super().__init__(session, households)
        self.bills = bills

    def list(
        self,
        household_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
        status: str | None,
        due_from: date | None,
        due_to: date | None,
    ) -> list[Bill]:
        self.require_household(household_id)
        return self.bills.list_active(
            household_id,
            limit=limit,
            offset=offset,
            status=status,
            due_from=due_from,
            due_to=due_to,
        )

    def get(self, household_id: uuid.UUID, bill_id: uuid.UUID) -> Bill:
        self.require_household(household_id)
        bill = self.bills.get_for_household(household_id, bill_id)
        if bill is None:
            raise NotFoundError("Bill not found.")
        return bill

    def create(self, household_id: uuid.UUID, payload: BillCreate) -> Bill:
        self.require_household(household_id)
        bill = self.bills.add(Bill(household_id=household_id, **payload.model_dump()))
        self.commit()
        self.session.refresh(bill)
        return bill

    def update(self, household_id: uuid.UUID, bill_id: uuid.UUID, payload: BillUpdate) -> Bill:
        bill = self.get(household_id, bill_id)
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            if isinstance(value, Enum):
                value = value.value
            setattr(bill, field, value)
        if bill.recurring and not bill.recurrence_rule:
            self.session.rollback()
            raise DomainValidationError("recurrence_rule is required when recurring is true.")
        if not bill.recurring and bill.recurrence_rule is not None:
            self.session.rollback()
            raise DomainValidationError("recurrence_rule must be omitted when recurring is false.")
        self.commit()
        self.session.refresh(bill)
        return bill

    def delete(self, household_id: uuid.UUID, bill_id: uuid.UUID) -> None:
        bill = self.get(household_id, bill_id)
        self.bills.soft_delete(bill)
        self.commit()


class DashboardService:
    def __init__(
        self,
        households: HouseholdRepository,
        envelopes: EnvelopeRepository,
        transactions: TransactionRepository,
        remittances: RemittanceRepository,
        bills: BillRepository,
    ) -> None:
        self.households = households
        self.envelopes = envelopes
        self.transactions = transactions
        self.remittances = remittances
        self.bills = bills

    def summary(self, household_id: uuid.UUID, *, due_within_days: int) -> dict:
        household = self.households.get_active(household_id)
        if household is None:
            raise NotFoundError("Household not found.")

        as_of = date.today()
        month_start = as_of.replace(day=1)
        due_through = as_of + timedelta(days=due_within_days)
        envelopes = self.envelopes.list_active(household_id, limit=100, offset=0)
        upcoming_bills = self.bills.list_active(
            household_id,
            limit=100,
            offset=0,
            status="scheduled",
            due_from=as_of,
            due_to=due_through,
        )
        target_total, balance_total = self.envelopes.totals(household_id)
        period_amounts = self.transactions.amounts_for_period(
            household_id, start_date=month_start, end_date=as_of
        )
        spent = (
            period_amounts.get("expense", Decimal("0"))
            + period_amounts.get("adjustment", Decimal("0"))
            - period_amounts.get("refund", Decimal("0"))
        )
        upcoming_total, upcoming_count = self.bills.upcoming_totals(
            household_id, due_from=as_of, due_to=due_through
        )
        return {
            "household": household,
            "as_of": as_of,
            "total_envelope_target_php": target_total,
            "total_envelope_balance_php": balance_total,
            "total_remitted_php": self.remittances.total_for_household(household_id),
            "total_spent_this_month_php": max(spent, Decimal("0")),
            "total_upcoming_bills_php": upcoming_total,
            "upcoming_bill_count": upcoming_count,
            "envelopes": envelopes,
            "upcoming_bills": upcoming_bills,
            "recent_transactions": self.transactions.list_active(
                household_id, limit=5, offset=0
            ),
        }

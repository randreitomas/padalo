from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.bill import Bill
from app.models.envelope import Envelope
from app.models.membership import HouseholdMember
from app.models.remittance import Remittance
from app.models.transaction import Transaction


class HouseholdMemberRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_active_for_household(
        self, household_id: uuid.UUID, member_id: uuid.UUID
    ) -> HouseholdMember | None:
        statement = select(HouseholdMember).where(
            HouseholdMember.id == member_id,
            HouseholdMember.household_id == household_id,
            HouseholdMember.deleted_at.is_(None),
            HouseholdMember.status == "active",
        )
        return self.session.scalar(statement)


class EnvelopeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(self, household_id: uuid.UUID, *, limit: int, offset: int) -> list[Envelope]:
        statement = (
            select(Envelope)
            .where(Envelope.household_id == household_id, Envelope.deleted_at.is_(None))
            .order_by(Envelope.sort_order, Envelope.created_at)
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(statement))

    def get_for_household(
        self, household_id: uuid.UUID, envelope_id: uuid.UUID, *, include_deleted: bool = False
    ) -> Envelope | None:
        statement = select(Envelope).where(
            Envelope.id == envelope_id,
            Envelope.household_id == household_id,
        )
        if not include_deleted:
            statement = statement.where(Envelope.deleted_at.is_(None))
        return self.session.scalar(statement)

    def add(self, envelope: Envelope) -> Envelope:
        self.session.add(envelope)
        return envelope

    def totals(self, household_id: uuid.UUID) -> tuple[Decimal, Decimal]:
        statement = select(
            func.coalesce(func.sum(Envelope.target_amount_php), 0),
            func.coalesce(func.sum(Envelope.current_balance_php), 0),
        ).where(Envelope.household_id == household_id, Envelope.deleted_at.is_(None))
        target, balance = self.session.execute(statement).one()
        return Decimal(target), Decimal(balance)

    def soft_delete(self, envelope: Envelope) -> None:
        envelope.deleted_at = datetime.now(UTC)


class TransactionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(
        self,
        household_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
        envelope_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Transaction]:
        statement: Select[tuple[Transaction]] = select(Transaction).where(
            Transaction.household_id == household_id,
            Transaction.deleted_at.is_(None),
        )
        if envelope_id is not None:
            statement = statement.where(Transaction.envelope_id == envelope_id)
        if start_date is not None:
            statement = statement.where(Transaction.occurred_on >= start_date)
        if end_date is not None:
            statement = statement.where(Transaction.occurred_on <= end_date)
        statement = statement.order_by(
            Transaction.occurred_on.desc(), Transaction.created_at.desc()
        )
        return list(self.session.scalars(statement.limit(limit).offset(offset)))

    def get_for_household(
        self, household_id: uuid.UUID, transaction_id: uuid.UUID
    ) -> Transaction | None:
        statement = select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.household_id == household_id,
            Transaction.deleted_at.is_(None),
        )
        return self.session.scalar(statement)

    def add(self, transaction: Transaction) -> Transaction:
        self.session.add(transaction)
        return transaction

    def amounts_for_period(
        self, household_id: uuid.UUID, *, start_date: date, end_date: date
    ) -> dict[str, Decimal]:
        statement = (
            select(
                Transaction.transaction_type,
                func.coalesce(func.sum(Transaction.amount_php), 0),
            )
            .where(
                Transaction.household_id == household_id,
                Transaction.deleted_at.is_(None),
                Transaction.occurred_on >= start_date,
                Transaction.occurred_on <= end_date,
            )
            .group_by(Transaction.transaction_type)
        )
        return {
            transaction_type: Decimal(amount)
            for transaction_type, amount in self.session.execute(statement)
        }

    def soft_delete(self, transaction: Transaction) -> None:
        transaction.deleted_at = datetime.now(UTC)


class RemittanceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(
        self,
        household_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[Remittance]:
        statement: Select[tuple[Remittance]] = select(Remittance).where(
            Remittance.household_id == household_id,
            Remittance.deleted_at.is_(None),
        )
        if start_at is not None:
            statement = statement.where(Remittance.sent_at >= start_at)
        if end_at is not None:
            statement = statement.where(Remittance.sent_at <= end_at)
        statement = statement.order_by(Remittance.sent_at.desc(), Remittance.created_at.desc())
        return list(self.session.scalars(statement.limit(limit).offset(offset)))

    def get_for_household(
        self, household_id: uuid.UUID, remittance_id: uuid.UUID
    ) -> Remittance | None:
        statement = select(Remittance).where(
            Remittance.id == remittance_id,
            Remittance.household_id == household_id,
            Remittance.deleted_at.is_(None),
        )
        return self.session.scalar(statement)

    def add(self, remittance: Remittance) -> Remittance:
        self.session.add(remittance)
        return remittance

    def total_for_household(self, household_id: uuid.UUID) -> Decimal:
        statement = select(func.coalesce(func.sum(Remittance.amount_php), 0)).where(
            Remittance.household_id == household_id,
            Remittance.deleted_at.is_(None),
        )
        return Decimal(self.session.scalar(statement))

    def soft_delete(self, remittance: Remittance) -> None:
        remittance.deleted_at = datetime.now(UTC)


class BillRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(
        self,
        household_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
        status: str | None = None,
        due_from: date | None = None,
        due_to: date | None = None,
    ) -> list[Bill]:
        statement: Select[tuple[Bill]] = select(Bill).where(
            Bill.household_id == household_id,
            Bill.deleted_at.is_(None),
        )
        if status is not None:
            statement = statement.where(Bill.status == status)
        if due_from is not None:
            statement = statement.where(Bill.due_date >= due_from)
        if due_to is not None:
            statement = statement.where(Bill.due_date <= due_to)
        statement = statement.order_by(Bill.due_date, Bill.created_at)
        return list(self.session.scalars(statement.limit(limit).offset(offset)))

    def get_for_household(self, household_id: uuid.UUID, bill_id: uuid.UUID) -> Bill | None:
        statement = select(Bill).where(
            Bill.id == bill_id,
            Bill.household_id == household_id,
            Bill.deleted_at.is_(None),
        )
        return self.session.scalar(statement)

    def add(self, bill: Bill) -> Bill:
        self.session.add(bill)
        return bill

    def upcoming_totals(
        self, household_id: uuid.UUID, *, due_from: date, due_to: date
    ) -> tuple[Decimal, int]:
        statement = select(
            func.coalesce(func.sum(Bill.amount_php), 0),
            func.count(Bill.id),
        ).where(
            Bill.household_id == household_id,
            Bill.deleted_at.is_(None),
            Bill.status == "scheduled",
            Bill.due_date >= due_from,
            Bill.due_date <= due_to,
        )
        amount, count = self.session.execute(statement).one()
        return Decimal(amount), int(count)

    def soft_delete(self, bill: Bill) -> None:
        bill.deleted_at = datetime.now(UTC)

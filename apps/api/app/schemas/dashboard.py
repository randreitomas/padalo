from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.schemas.bills import BillRead
from app.schemas.common import APIModel
from app.schemas.envelopes import EnvelopeRead
from app.schemas.households import HouseholdRead
from app.schemas.transactions import TransactionRead


class DashboardSummaryRead(APIModel):
    household: HouseholdRead
    as_of: date
    total_envelope_target_php: Decimal
    total_envelope_balance_php: Decimal
    total_remitted_php: Decimal
    total_spent_this_month_php: Decimal
    total_upcoming_bills_php: Decimal
    upcoming_bill_count: int
    envelopes: list[EnvelopeRead]
    upcoming_bills: list[BillRead]
    recent_transactions: list[TransactionRead]

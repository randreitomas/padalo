from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.bills import BillCreate
from app.schemas.households import HouseholdCreate, HouseholdUpdate
from app.schemas.transactions import TransactionCreate


def test_household_codes_are_normalized() -> None:
    payload = HouseholdCreate(name="  Santos Household  ", base_currency="php", home_country="ph")

    assert payload.name == "Santos Household"
    assert payload.base_currency == "PHP"
    assert payload.home_country == "PH"


def test_empty_household_update_is_rejected() -> None:
    with pytest.raises(ValidationError, match="At least one field"):
        HouseholdUpdate()


def test_recurring_bill_requires_a_recurrence_rule() -> None:
    with pytest.raises(ValidationError, match="recurrence_rule is required"):
        BillCreate(
            name="Rent",
            amount_php=Decimal("12000.00"),
            due_date=date(2026, 7, 31),
            recurring=True,
        )


def test_transaction_amount_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        TransactionCreate(amount_php=Decimal("0.00"), occurred_on=date(2026, 7, 17))

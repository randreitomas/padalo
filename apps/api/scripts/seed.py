from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

import app.models  # noqa: F401
from app.database import create_database_engine, metadata

DEMO_CREATED_AT = datetime(2026, 7, 1, 8, 0, tzinfo=UTC)
DEMO_NOW = datetime(2026, 7, 17, 9, 0, tzinfo=UTC)

ROLE_IDS = {
    "worker": uuid.UUID("11111111-1111-4111-8111-111111111111"),
    "family_member": uuid.UUID("22222222-2222-4222-8222-222222222222"),
    "coordinator": uuid.UUID("33333333-3333-4333-8333-333333333333"),
}

USER_IDS = {
    "maria_worker": uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
    "ana_family": uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
    "jose_coordinator": uuid.UUID("ffffffff-ffff-4fff-8fff-ffffffffffff"),
}

HOUSEHOLD_ID = uuid.UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")

MEMBER_IDS = {
    "maria_worker": uuid.UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
    "ana_family": uuid.UUID("eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"),
    "jose_coordinator": uuid.UUID("99999999-9999-4999-8999-999999999999"),
}

ENVELOPE_IDS = {
    "groceries": uuid.UUID("10000000-0000-4000-8000-000000000001"),
    "bills": uuid.UUID("10000000-0000-4000-8000-000000000002"),
    "education": uuid.UUID("10000000-0000-4000-8000-000000000003"),
    "savings": uuid.UUID("10000000-0000-4000-8000-000000000004"),
    "transportation": uuid.UUID("10000000-0000-4000-8000-000000000005"),
}


def timestamped_row(**row: object) -> dict[str, object]:
    return {
        "created_at": DEMO_CREATED_AT,
        "updated_at": DEMO_NOW,
        **row,
    }


def active_row(**row: object) -> dict[str, object]:
    return {**timestamped_row(**row), "deleted_at": None}


def build_role_rows() -> list[dict[str, object]]:
    return [
        timestamped_row(
            id=ROLE_IDS["worker"],
            key="worker",
            name="Worker",
            description="OFW sender who contributes remittances and monitors household cash flow.",
            sort_order=10,
            is_system=True,
        ),
        timestamped_row(
            id=ROLE_IDS["family_member"],
            key="family_member",
            name="Family Member",
            description="Household member who logs expenses and views envelope balances.",
            sort_order=20,
            is_system=True,
        ),
        timestamped_row(
            id=ROLE_IDS["coordinator"],
            key="coordinator",
            name="Coordinator",
            description="Household coordinator who manages envelopes, bills, and members.",
            sort_order=30,
            is_system=True,
        ),
    ]


def upsert_roles(connection) -> None:
    roles = metadata.tables["roles"]
    rows = build_role_rows()

    for row in rows:
        statement = insert(roles).values(row)
        connection.execute(
            statement.on_conflict_do_update(
                index_elements=["key"],
                set_={
                    field: getattr(statement.excluded, field)
                    for field in row
                    if field not in {"id", "key"}
                },
            )
        )


def reset_demo_household(connection) -> None:
    """Remove only the deterministic demo household before recreating its fixed scenario."""

    households = metadata.tables["households"]
    connection.execute(households.delete().where(households.c.id == HOUSEHOLD_ID))


def upsert_demo_rows(connection) -> None:
    for table, rows in build_demo_groups():
        for row in rows:
            statement = insert(table).values(row)
            connection.execute(
                statement.on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        field: getattr(statement.excluded, field)
                        for field in row
                        if field != "id"
                    },
                )
            )


def reset_local_demo_database(engine: Engine) -> None:
    """Recreate the development-only SQLite database with the fixed Santos Family scenario."""

    if engine.dialect.name != "sqlite":
        raise ValueError("Local demo bootstrap requires a SQLite database.")

    metadata.drop_all(engine)
    metadata.create_all(engine)

    with engine.begin() as connection:
        connection.execute(metadata.tables["roles"].insert(), build_role_rows())
        for table, rows in build_demo_groups():
            connection.execute(table.insert(), rows)


def build_demo_groups() -> list[tuple[object, list[dict[str, object]]]]:
    users = metadata.tables["users"]
    households = metadata.tables["households"]
    members = metadata.tables["household_members"]
    envelopes = metadata.tables["envelopes"]
    transactions = metadata.tables["transactions"]
    remittances = metadata.tables["remittances"]
    bills = metadata.tables["bills"]
    forecast_history = metadata.tables["forecast_history"]

    return [
        (
            users,
            [
                active_row(
                    id=USER_IDS["maria_worker"],
                    auth_provider="demo",
                    auth_subject="demo-maria-santos",
                    email="maria.santos@example.test",
                    display_name="Maria Santos",
                    locale="en-AE",
                    timezone="Asia/Dubai",
                ),
                active_row(
                    id=USER_IDS["ana_family"],
                    auth_provider="demo",
                    auth_subject="demo-ana-santos",
                    email="ana.santos@example.test",
                    display_name="Ana Santos",
                    locale="en-PH",
                    timezone="Asia/Manila",
                ),
                active_row(
                    id=USER_IDS["jose_coordinator"],
                    auth_provider="demo",
                    auth_subject="demo-jose-santos",
                    email="jose.santos@example.test",
                    display_name="Jose Santos",
                    locale="en-PH",
                    timezone="Asia/Manila",
                ),
            ],
        ),
        (
            households,
            [
                active_row(
                    id=HOUSEHOLD_ID,
                    name="Santos Family",
                    base_currency="PHP",
                    home_country="PH",
                    created_by_user_id=USER_IDS["maria_worker"],
                )
            ],
        ),
        (
            members,
            [
                active_row(
                    id=MEMBER_IDS["maria_worker"],
                    household_id=HOUSEHOLD_ID,
                    user_id=USER_IDS["maria_worker"],
                    role_id=ROLE_IDS["worker"],
                    status="active",
                    joined_at=DEMO_NOW,
                ),
                active_row(
                    id=MEMBER_IDS["ana_family"],
                    household_id=HOUSEHOLD_ID,
                    user_id=USER_IDS["ana_family"],
                    role_id=ROLE_IDS["family_member"],
                    invited_by_user_id=USER_IDS["maria_worker"],
                    status="active",
                    joined_at=DEMO_NOW,
                ),
                active_row(
                    id=MEMBER_IDS["jose_coordinator"],
                    household_id=HOUSEHOLD_ID,
                    user_id=USER_IDS["jose_coordinator"],
                    role_id=ROLE_IDS["coordinator"],
                    invited_by_user_id=USER_IDS["maria_worker"],
                    status="active",
                    joined_at=DEMO_NOW,
                ),
            ],
        ),
        (
            envelopes,
            [
                active_row(
                    id=ENVELOPE_IDS["groceries"],
                    household_id=HOUSEHOLD_ID,
                    name="Groceries",
                    target_amount_php=Decimal("8000.00"),
                    current_balance_php=Decimal("5350.00"),
                    sort_order=10,
                ),
                active_row(
                    id=ENVELOPE_IDS["education"],
                    household_id=HOUSEHOLD_ID,
                    name="Education",
                    target_amount_php=Decimal("12000.00"),
                    current_balance_php=Decimal("6250.00"),
                    sort_order=20,
                ),
                active_row(
                    id=ENVELOPE_IDS["bills"],
                    household_id=HOUSEHOLD_ID,
                    name="Bills",
                    target_amount_php=Decimal("5000.00"),
                    current_balance_php=Decimal("2481.00"),
                    sort_order=30,
                ),
                active_row(
                    id=ENVELOPE_IDS["savings"],
                    household_id=HOUSEHOLD_ID,
                    name="Savings",
                    target_amount_php=Decimal("10000.00"),
                    current_balance_php=Decimal("8000.00"),
                    sort_order=40,
                ),
                active_row(
                    id=ENVELOPE_IDS["transportation"],
                    household_id=HOUSEHOLD_ID,
                    name="Transportation",
                    target_amount_php=Decimal("3000.00"),
                    current_balance_php=Decimal("2300.00"),
                    sort_order=50,
                ),
            ],
        ),
        (
            remittances,
            [
                active_row(
                    id=uuid.UUID("20000000-0000-4000-8000-000000000001"),
                    household_id=HOUSEHOLD_ID,
                    recorded_by_member_id=MEMBER_IDS["maria_worker"],
                    amount_php=Decimal("20000.00"),
                    source_amount=Decimal("1266.00"),
                    source_currency="AED",
                    provider="Wise",
                    fee_php=Decimal("210.00"),
                    rate_used=Decimal("15.79778831"),
                    sent_at=datetime(2026, 7, 15, 18, 15, tzinfo=UTC),
                ),
                active_row(
                    id=uuid.UUID("20000000-0000-4000-8000-000000000002"),
                    household_id=HOUSEHOLD_ID,
                    recorded_by_member_id=MEMBER_IDS["maria_worker"],
                    amount_php=Decimal("18000.00"),
                    source_amount=Decimal("1140.00"),
                    source_currency="AED",
                    provider="Remitly",
                    fee_php=Decimal("180.00"),
                    rate_used=Decimal("15.78947368"),
                    sent_at=datetime(2026, 7, 2, 18, 15, tzinfo=UTC),
                ),
            ],
        ),
        (
            transactions,
            [
                active_row(
                    id=uuid.UUID("30000000-0000-4000-8000-000000000001"),
                    household_id=HOUSEHOLD_ID,
                    envelope_id=ENVELOPE_IDS["groceries"],
                    logged_by_member_id=MEMBER_IDS["ana_family"],
                    amount_php=Decimal("1650.00"),
                    transaction_type="expense",
                    source="manual",
                    merchant="SM Supermarket",
                    note="Weekly family groceries",
                    occurred_on=date(2026, 7, 17),
                ),
                active_row(
                    id=uuid.UUID("30000000-0000-4000-8000-000000000002"),
                    household_id=HOUSEHOLD_ID,
                    envelope_id=ENVELOPE_IDS["groceries"],
                    logged_by_member_id=MEMBER_IDS["ana_family"],
                    amount_php=Decimal("1000.00"),
                    transaction_type="expense",
                    source="manual",
                    merchant="Mercury Drug",
                    note="Medicine and household health supplies",
                    occurred_on=date(2026, 7, 15),
                ),
                active_row(
                    id=uuid.UUID("30000000-0000-4000-8000-000000000003"),
                    household_id=HOUSEHOLD_ID,
                    envelope_id=ENVELOPE_IDS["education"],
                    logged_by_member_id=MEMBER_IDS["ana_family"],
                    amount_php=Decimal("1250.00"),
                    transaction_type="expense",
                    source="manual",
                    merchant="National Book Store",
                    note="School supplies",
                    occurred_on=date(2026, 7, 13),
                ),
                active_row(
                    id=uuid.UUID("30000000-0000-4000-8000-000000000004"),
                    household_id=HOUSEHOLD_ID,
                    envelope_id=ENVELOPE_IDS["bills"],
                    logged_by_member_id=MEMBER_IDS["jose_coordinator"],
                    amount_php=Decimal("620.00"),
                    transaction_type="expense",
                    source="manual",
                    merchant="Water Bill",
                    note="Water District payment",
                    occurred_on=date(2026, 7, 11),
                ),
                active_row(
                    id=uuid.UUID("30000000-0000-4000-8000-000000000005"),
                    household_id=HOUSEHOLD_ID,
                    envelope_id=ENVELOPE_IDS["bills"],
                    logged_by_member_id=MEMBER_IDS["jose_coordinator"],
                    amount_php=Decimal("1899.00"),
                    transaction_type="expense",
                    source="manual",
                    merchant="Internet Bill",
                    note="Converge monthly service",
                    occurred_on=date(2026, 7, 10),
                ),
                active_row(
                    id=uuid.UUID("30000000-0000-4000-8000-000000000006"),
                    household_id=HOUSEHOLD_ID,
                    envelope_id=ENVELOPE_IDS["education"],
                    logged_by_member_id=MEMBER_IDS["ana_family"],
                    amount_php=Decimal("4500.00"),
                    transaction_type="expense",
                    source="manual",
                    merchant="Tuition Payment",
                    note="Partial tuition payment",
                    occurred_on=date(2026, 7, 6),
                ),
                active_row(
                    id=uuid.UUID("30000000-0000-4000-8000-000000000007"),
                    household_id=HOUSEHOLD_ID,
                    envelope_id=ENVELOPE_IDS["transportation"],
                    logged_by_member_id=MEMBER_IDS["ana_family"],
                    amount_php=Decimal("700.00"),
                    transaction_type="expense",
                    source="manual",
                    merchant="Transportation",
                    note="School and household travel",
                    occurred_on=date(2026, 7, 4),
                ),
                active_row(
                    id=uuid.UUID("30000000-0000-4000-8000-000000000008"),
                    household_id=HOUSEHOLD_ID,
                    envelope_id=ENVELOPE_IDS["savings"],
                    logged_by_member_id=MEMBER_IDS["jose_coordinator"],
                    amount_php=Decimal("2000.00"),
                    transaction_type="adjustment",
                    source="manual",
                    merchant="Savings reserve",
                    note="Moved into the household savings reserve",
                    occurred_on=date(2026, 7, 2),
                ),
            ],
        ),
        (
            bills,
            [
                active_row(
                    id=uuid.UUID("40000000-0000-4000-8000-000000000001"),
                    household_id=HOUSEHOLD_ID,
                    name="Meralco",
                    amount_php=Decimal("2450.00"),
                    due_date=date(2026, 7, 19),
                    category="Bills",
                    recurring=True,
                    recurrence_rule="monthly",
                    status="scheduled",
                ),
                active_row(
                    id=uuid.UUID("40000000-0000-4000-8000-000000000002"),
                    household_id=HOUSEHOLD_ID,
                    name="Converge",
                    amount_php=Decimal("1899.00"),
                    due_date=date(2026, 7, 21),
                    category="Bills",
                    recurring=True,
                    recurrence_rule="monthly",
                    status="scheduled",
                ),
                active_row(
                    id=uuid.UUID("40000000-0000-4000-8000-000000000003"),
                    household_id=HOUSEHOLD_ID,
                    name="Tuition",
                    amount_php=Decimal("7500.00"),
                    due_date=date(2026, 7, 24),
                    category="Education",
                    recurring=False,
                    recurrence_rule=None,
                    status="scheduled",
                ),
                active_row(
                    id=uuid.UUID("40000000-0000-4000-8000-000000000004"),
                    household_id=HOUSEHOLD_ID,
                    name="Water District",
                    amount_php=Decimal("620.00"),
                    due_date=date(2026, 7, 26),
                    category="Bills",
                    recurring=True,
                    recurrence_rule="monthly",
                    status="scheduled",
                ),
            ],
        ),
        (
            forecast_history,
            [
                timestamped_row(
                    id=uuid.UUID("50000000-0000-4000-8000-000000000001"),
                    household_id=HOUSEHOLD_ID,
                    requested_by_member_id=MEMBER_IDS["maria_worker"],
                    provider="Wise",
                    amount_php=Decimal("15000.00"),
                    recommended_send_date=date(2026, 7, 23),
                    recommended_day="Thursday",
                    expected_savings_php=Decimal("112.50"),
                    confidence=Decimal("0.8500"),
                    model_version="seed-placeholder-v1",
                    baseline_strategy="naive_last_observed_fee",
                    generated_at=datetime(2026, 7, 17, 8, 0, tzinfo=UTC),
                )
            ],
        ),
    ]


def main() -> None:
    engine = create_database_engine()
    if engine is None:
        raise SystemExit("DATABASE_URL is not configured. Set it before running the seed script.")

    if engine.dialect.name == "sqlite":
        reset_local_demo_database(engine)
    else:
        with engine.begin() as connection:
            upsert_roles(connection)
            reset_demo_household(connection)
            upsert_demo_rows(connection)

    print("Santos Family demo data reset and inserted.")


if __name__ == "__main__":
    main()

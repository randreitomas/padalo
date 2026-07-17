from datetime import date
from decimal import Decimal

from sqlalchemy.dialects import postgresql

from scripts.seed import (
    DEMO_CREATED_AT,
    DEMO_NOW,
    HOUSEHOLD_ID,
    ROLE_IDS,
    build_demo_groups,
    reset_demo_household,
    upsert_demo_rows,
    upsert_roles,
)


class StatementRecorder:
    def __init__(self) -> None:
        self.statements: list[object] = []

    def execute(self, statement) -> None:
        self.statements.append(statement)


def demo_rows_by_table() -> dict[str, list[dict[str, object]]]:
    return {table.name: rows for table, rows in build_demo_groups()}


def test_santos_family_demo_seed_matches_the_judge_scenario() -> None:
    rows = demo_rows_by_table()

    assert rows["households"] == [
        {
            "created_at": DEMO_CREATED_AT,
            "updated_at": DEMO_NOW,
            "deleted_at": None,
            "id": HOUSEHOLD_ID,
            "name": "Santos Family",
            "base_currency": "PHP",
            "home_country": "PH",
            "created_by_user_id": rows["users"][0]["id"],
        }
    ]

    assert {user["display_name"] for user in rows["users"]} == {
        "Maria Santos",
        "Ana Santos",
        "Jose Santos",
    }
    assert {member["role_id"] for member in rows["household_members"]} == set(ROLE_IDS.values())

    targets = {envelope["name"]: envelope["target_amount_php"] for envelope in rows["envelopes"]}
    assert targets == {
        "Groceries": Decimal("8000.00"),
        "Education": Decimal("12000.00"),
        "Bills": Decimal("5000.00"),
        "Savings": Decimal("10000.00"),
        "Transportation": Decimal("3000.00"),
    }

    assert {transaction["merchant"] for transaction in rows["transactions"]} >= {
        "SM Supermarket",
        "Mercury Drug",
        "National Book Store",
        "Water Bill",
        "Internet Bill",
        "Tuition Payment",
    }
    assert [(bill["name"], bill["due_date"]) for bill in rows["bills"]] == [
        ("Meralco", date(2026, 7, 19)),
        ("Converge", date(2026, 7, 21)),
        ("Tuition", date(2026, 7, 24)),
        ("Water District", date(2026, 7, 26)),
    ]


def test_demo_seed_rows_use_fixed_timestamps() -> None:
    for _, table_rows in build_demo_groups():
        for row in table_rows:
            assert row["created_at"] == DEMO_CREATED_AT
            assert row["updated_at"] == DEMO_NOW


def test_demo_seed_statements_compile_for_postgres() -> None:
    recorder = StatementRecorder()

    upsert_roles(recorder)
    reset_demo_household(recorder)
    upsert_demo_rows(recorder)

    assert len(recorder.statements) == 31
    for statement in recorder.statements:
        str(statement.compile(dialect=postgresql.dialect()))

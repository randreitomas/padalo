"""phase 1 database foundation

Revision ID: 202607170001
Revises:
Create Date: 2026-07-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202607170001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        nullable=False,
    )


def timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    ]


def soft_delete() -> sa.Column:
    return sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "users",
        uuid_pk(),
        *timestamps(),
        soft_delete(),
        sa.Column("auth_provider", sa.String(length=32), nullable=False),
        sa.Column("auth_subject", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("avatar_url", sa.String(length=2048), nullable=True),
        sa.Column("locale", sa.String(length=16), server_default="en-PH", nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default="Asia/Manila", nullable=False),
        sa.CheckConstraint(
            "length(auth_provider) > 0", name=op.f("ck_users_auth_provider_not_empty")
        ),
        sa.CheckConstraint(
            "length(auth_subject) > 0", name=op.f("ck_users_auth_subject_not_empty")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(
        "ix_users_auth_provider_auth_subject", "users", ["auth_provider", "auth_subject"]
    )
    op.create_index(
        "uq_users_auth_provider_auth_subject",
        "users",
        ["auth_provider", "auth_subject"],
        unique=True,
    )
    op.create_index(
        "uq_users_email_active",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("email IS NOT NULL AND deleted_at IS NULL"),
    )

    op.create_table(
        "roles",
        uuid_pk(),
        *timestamps(),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_system", sa.Boolean(), server_default="true", nullable=False),
        sa.CheckConstraint("length(key) > 0", name=op.f("ck_roles_key_not_empty")),
        sa.CheckConstraint("length(name) > 0", name=op.f("ck_roles_name_not_empty")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roles")),
    )
    op.create_index("uq_roles_key", "roles", ["key"], unique=True)

    op.create_table(
        "households",
        uuid_pk(),
        *timestamps(),
        soft_delete(),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("base_currency", sa.String(length=3), server_default="PHP", nullable=False),
        sa.Column("home_country", sa.String(length=2), server_default="PH", nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint("length(name) > 0", name=op.f("ck_households_name_not_empty")),
        sa.CheckConstraint(
            "length(base_currency) = 3", name=op.f("ck_households_base_currency_iso_4217")
        ),
        sa.CheckConstraint(
            "length(home_country) = 2",
            name=op.f("ck_households_home_country_iso_3166_alpha_2"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("fk_households_created_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_households")),
    )
    op.create_index("ix_households_created_by_user_id", "households", ["created_by_user_id"])

    op.create_table(
        "household_members",
        uuid_pk(),
        *timestamps(),
        soft_delete(),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invited_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=24), server_default="active", nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('invited', 'active', 'removed')",
            name=op.f("ck_household_members_status_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
            name=op.f("fk_household_members_household_id_households"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_household_members_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name=op.f("fk_household_members_role_id_roles"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["invited_by_user_id"],
            ["users.id"],
            name=op.f("fk_household_members_invited_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_household_members")),
    )
    op.create_index("ix_household_members_household_id", "household_members", ["household_id"])
    op.create_index("ix_household_members_user_id", "household_members", ["user_id"])
    op.create_index("ix_household_members_role_id", "household_members", ["role_id"])
    op.create_index("ix_household_members_status", "household_members", ["status"])
    op.create_index(
        "uq_household_members_household_id_user_id_active",
        "household_members",
        ["household_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "envelopes",
        uuid_pk(),
        *timestamps(),
        soft_delete(),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("target_amount_php", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column("current_balance_php", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.CheckConstraint("length(name) > 0", name=op.f("ck_envelopes_name_not_empty")),
        sa.CheckConstraint(
            "target_amount_php >= 0",
            name=op.f("ck_envelopes_target_amount_php_non_negative"),
        ),
        sa.CheckConstraint(
            "current_balance_php >= 0",
            name=op.f("ck_envelopes_current_balance_php_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
            name=op.f("fk_envelopes_household_id_households"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_envelopes")),
    )
    op.create_index("ix_envelopes_household_id", "envelopes", ["household_id"])
    op.create_index(
        "ix_envelopes_household_id_sort_order", "envelopes", ["household_id", "sort_order"]
    )
    op.create_index(
        "uq_envelopes_household_id_name_active",
        "envelopes",
        ["household_id", "name"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "transactions",
        uuid_pk(),
        *timestamps(),
        soft_delete(),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("envelope_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("logged_by_member_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("amount_php", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "transaction_type", sa.String(length=24), server_default="expense", nullable=False
        ),
        sa.Column("source", sa.String(length=24), server_default="manual", nullable=False),
        sa.Column("merchant", sa.String(length=160), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("receipt_url", sa.String(length=2048), nullable=True),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.CheckConstraint("amount_php > 0", name=op.f("ck_transactions_amount_php_positive")),
        sa.CheckConstraint(
            "transaction_type IN ('expense', 'refund', 'adjustment')",
            name=op.f("ck_transactions_transaction_type_valid"),
        ),
        sa.CheckConstraint(
            "source IN ('manual', 'chat', 'receipt')",
            name=op.f("ck_transactions_source_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
            name=op.f("fk_transactions_household_id_households"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["envelope_id"],
            ["envelopes.id"],
            name=op.f("fk_transactions_envelope_id_envelopes"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["logged_by_member_id"],
            ["household_members.id"],
            name=op.f("fk_transactions_logged_by_member_id_household_members"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_transactions")),
    )
    op.create_index(
        "ix_transactions_household_id_created_at",
        "transactions",
        ["household_id", "created_at"],
    )
    op.create_index(
        "ix_transactions_envelope_id_created_at",
        "transactions",
        ["envelope_id", "created_at"],
    )
    op.create_index("ix_transactions_logged_by_member_id", "transactions", ["logged_by_member_id"])

    op.create_table(
        "remittances",
        uuid_pk(),
        *timestamps(),
        soft_delete(),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recorded_by_member_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("amount_php", sa.Numeric(12, 2), nullable=False),
        sa.Column("source_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("source_currency", sa.String(length=3), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("fee_php", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column("rate_used", sa.Numeric(18, 8), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount_php > 0", name=op.f("ck_remittances_amount_php_positive")),
        sa.CheckConstraint("source_amount > 0", name=op.f("ck_remittances_source_amount_positive")),
        sa.CheckConstraint("fee_php >= 0", name=op.f("ck_remittances_fee_php_non_negative")),
        sa.CheckConstraint("rate_used > 0", name=op.f("ck_remittances_rate_used_positive")),
        sa.CheckConstraint(
            "length(source_currency) = 3", name=op.f("ck_remittances_source_currency_iso_4217")
        ),
        sa.CheckConstraint("length(provider) > 0", name=op.f("ck_remittances_provider_not_empty")),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
            name=op.f("fk_remittances_household_id_households"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recorded_by_member_id"],
            ["household_members.id"],
            name=op.f("fk_remittances_recorded_by_member_id_household_members"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_remittances")),
    )
    op.create_index(
        "ix_remittances_household_id_sent_at",
        "remittances",
        ["household_id", "sent_at"],
    )
    op.create_index(
        "ix_remittances_recorded_by_member_id", "remittances", ["recorded_by_member_id"]
    )
    op.create_index("ix_remittances_provider", "remittances", ["provider"])

    op.create_table(
        "bills",
        uuid_pk(),
        *timestamps(),
        soft_delete(),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("amount_php", sa.Numeric(12, 2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("recurring", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("recurrence_rule", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=24), server_default="scheduled", nullable=False),
        sa.CheckConstraint("length(name) > 0", name=op.f("ck_bills_name_not_empty")),
        sa.CheckConstraint("amount_php > 0", name=op.f("ck_bills_amount_php_positive")),
        sa.CheckConstraint(
            "status IN ('scheduled', 'paid', 'skipped')",
            name=op.f("ck_bills_status_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
            name=op.f("fk_bills_household_id_households"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bills")),
    )
    op.create_index("ix_bills_household_id_due_date", "bills", ["household_id", "due_date"])
    op.create_index("ix_bills_status", "bills", ["status"])

    op.create_table(
        "forecast_history",
        uuid_pk(),
        *timestamps(),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by_member_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("amount_php", sa.Numeric(12, 2), nullable=False),
        sa.Column("recommended_send_date", sa.Date(), nullable=False),
        sa.Column("recommended_day", sa.String(length=16), nullable=False),
        sa.Column("expected_savings_php", sa.Numeric(12, 2), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("model_version", sa.String(length=80), nullable=False),
        sa.Column("baseline_strategy", sa.String(length=120), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount_php > 0", name=op.f("ck_forecast_history_amount_php_positive")),
        sa.CheckConstraint(
            "expected_savings_php >= 0",
            name=op.f("ck_forecast_history_expected_savings_php_non_negative"),
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name=op.f("ck_forecast_history_confidence_between_zero_and_one"),
        ),
        sa.CheckConstraint(
            "length(provider) > 0", name=op.f("ck_forecast_history_provider_not_empty")
        ),
        sa.CheckConstraint(
            "length(model_version) > 0",
            name=op.f("ck_forecast_history_model_version_not_empty"),
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
            name=op.f("fk_forecast_history_household_id_households"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_member_id"],
            ["household_members.id"],
            name=op.f("fk_forecast_history_requested_by_member_id_household_members"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_forecast_history")),
    )
    op.create_index(
        "ix_forecast_history_household_id_generated_at",
        "forecast_history",
        ["household_id", "generated_at"],
    )
    op.create_index(
        "ix_forecast_history_requested_by_member_id",
        "forecast_history",
        ["requested_by_member_id"],
    )
    op.create_index("ix_forecast_history_provider", "forecast_history", ["provider"])


def downgrade() -> None:
    op.drop_index("ix_forecast_history_provider", table_name="forecast_history")
    op.drop_index("ix_forecast_history_requested_by_member_id", table_name="forecast_history")
    op.drop_index("ix_forecast_history_household_id_generated_at", table_name="forecast_history")
    op.drop_table("forecast_history")

    op.drop_index("ix_bills_status", table_name="bills")
    op.drop_index("ix_bills_household_id_due_date", table_name="bills")
    op.drop_table("bills")

    op.drop_index("ix_remittances_provider", table_name="remittances")
    op.drop_index("ix_remittances_recorded_by_member_id", table_name="remittances")
    op.drop_index("ix_remittances_household_id_sent_at", table_name="remittances")
    op.drop_table("remittances")

    op.drop_index("ix_transactions_logged_by_member_id", table_name="transactions")
    op.drop_index("ix_transactions_envelope_id_created_at", table_name="transactions")
    op.drop_index("ix_transactions_household_id_created_at", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("uq_envelopes_household_id_name_active", table_name="envelopes")
    op.drop_index("ix_envelopes_household_id_sort_order", table_name="envelopes")
    op.drop_index("ix_envelopes_household_id", table_name="envelopes")
    op.drop_table("envelopes")

    op.drop_index(
        "uq_household_members_household_id_user_id_active", table_name="household_members"
    )
    op.drop_index("ix_household_members_status", table_name="household_members")
    op.drop_index("ix_household_members_role_id", table_name="household_members")
    op.drop_index("ix_household_members_user_id", table_name="household_members")
    op.drop_index("ix_household_members_household_id", table_name="household_members")
    op.drop_table("household_members")

    op.drop_index("ix_households_created_by_user_id", table_name="households")
    op.drop_table("households")

    op.drop_index("uq_roles_key", table_name="roles")
    op.drop_table("roles")

    op.drop_index("uq_users_email_active", table_name="users")
    op.drop_index("uq_users_auth_provider_auth_subject", table_name="users")
    op.drop_index("ix_users_auth_provider_auth_subject", table_name="users")
    op.drop_table("users")

"""Create initial tables and default data

Revision ID: 0001
Revises:
Create Date: 2026-06-03
"""

from decimal import Decimal
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_USER_EMAIL = "user@example.com"
DEFAULT_USER_PASSWORD_HASH = (
    "pbkdf2_sha256$600000$default-user-salt$"
    "f3488d07413f42a7e2f4184f8fcccf0bb51505d37cbf327cb06706e4259d2a79"
)
DEFAULT_ADMIN_EMAIL = "admin@example.com"
DEFAULT_ADMIN_PASSWORD_HASH = (
    "pbkdf2_sha256$600000$default-admin-salt$"
    "a81b41b6faa04a9a984df2f3b440c76687dfb26f7d1859543039fa8a2537db7d"
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_admins_email", "admins", ["email"], unique=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("balance", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("transaction_id", sa.String(length=100), nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "account_id",
            sa.Integer(),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_payments_account_id", "payments", ["account_id"])
    op.create_index(
        "ix_payments_transaction_id",
        "payments",
        ["transaction_id"],
        unique=True,
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])

    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("email", sa.String()),
        sa.column("password_hash", sa.String()),
        sa.column("full_name", sa.String()),
    )
    admins_table = sa.table(
        "admins",
        sa.column("id", sa.Integer()),
        sa.column("email", sa.String()),
        sa.column("password_hash", sa.String()),
        sa.column("full_name", sa.String()),
    )
    accounts_table = sa.table(
        "accounts",
        sa.column("id", sa.Integer()),
        sa.column("user_id", sa.Integer()),
        sa.column("balance", sa.Numeric(12, 2)),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": 1,
                "email": DEFAULT_USER_EMAIL,
                "password_hash": DEFAULT_USER_PASSWORD_HASH,
                "full_name": "Test User",
            }
        ],
    )
    op.bulk_insert(
        admins_table,
        [
            {
                "id": 1,
                "email": DEFAULT_ADMIN_EMAIL,
                "password_hash": DEFAULT_ADMIN_PASSWORD_HASH,
                "full_name": "Test Admin",
            }
        ],
    )
    op.bulk_insert(
        accounts_table,
        [
            {
                "id": 1,
                "user_id": 1,
                "balance": Decimal("0.00"),
            }
        ],
    )

    op.execute(
        "SELECT setval(pg_get_serial_sequence('users', 'id'), "
        "(SELECT MAX(id) FROM users))"
    )
    op.execute(
        "SELECT setval(pg_get_serial_sequence('admins', 'id'), "
        "(SELECT MAX(id) FROM admins))"
    )
    op.execute(
        "SELECT setval(pg_get_serial_sequence('accounts', 'id'), "
        "(SELECT MAX(id) FROM accounts))"
    )


def downgrade() -> None:
    op.drop_index("ix_payments_user_id", table_name="payments")
    op.drop_index("ix_payments_transaction_id", table_name="payments")
    op.drop_index("ix_payments_account_id", table_name="payments")
    op.drop_table("payments")

    op.drop_index("ix_accounts_user_id", table_name="accounts")
    op.drop_table("accounts")

    op.drop_index("ix_admins_email", table_name="admins")
    op.drop_table("admins")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

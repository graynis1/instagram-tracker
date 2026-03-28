"""rename check_interval_hours to check_interval_minutes

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tracked_accounts",
        sa.Column("check_interval_minutes", sa.Integer(), nullable=True),
    )
    # Eski saat değerlerini dakikaya çevir (varsa)
    op.execute(
        "UPDATE tracked_accounts SET check_interval_minutes = check_interval_hours * 60 "
        "WHERE check_interval_hours IS NOT NULL"
    )
    # Null kalan satırları varsayılan 360 dk (6 saat) yap
    op.execute(
        "UPDATE tracked_accounts SET check_interval_minutes = 360 "
        "WHERE check_interval_minutes IS NULL"
    )
    op.alter_column("tracked_accounts", "check_interval_minutes", nullable=False)
    op.drop_column("tracked_accounts", "check_interval_hours")


def downgrade() -> None:
    op.add_column(
        "tracked_accounts",
        sa.Column("check_interval_hours", sa.Integer(), nullable=True),
    )
    op.execute(
        "UPDATE tracked_accounts SET check_interval_hours = GREATEST(1, check_interval_minutes / 60)"
    )
    op.alter_column("tracked_accounts", "check_interval_hours", nullable=False)
    op.drop_column("tracked_accounts", "check_interval_minutes")

"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_token", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tracked_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("instagram_username", sa.String(), nullable=False),
        sa.Column("check_interval_hours", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "account_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tracked_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("followers_count", sa.Integer(), nullable=True),
        sa.Column("following_count", sa.Integer(), nullable=True),
        sa.Column("posts_count", sa.Integer(), nullable=True),
        sa.Column("is_private", sa.Boolean(), nullable=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("biography", sa.Text(), nullable=True),
        sa.Column("external_url", sa.String(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("profile_pic_url", sa.String(), nullable=True),
        sa.Column("snapshotted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tracked_account_id"], ["tracked_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "follower_changes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tracked_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "change_type",
            sa.Enum(
                "new_follower", "lost_follower", "new_following", "lost_following",
                name="changetype",
            ),
            nullable=False,
        ),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("profile_pic_url", sa.String(), nullable=True),
        sa.Column("detected_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tracked_account_id"], ["tracked_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "notifications_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tracked_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notification_type", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("was_delivered", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["tracked_account_id"], ["tracked_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # İndeksler
    op.create_index("ix_tracked_accounts_user_id", "tracked_accounts", ["user_id"])
    op.create_index("ix_tracked_accounts_username", "tracked_accounts", ["instagram_username"])
    op.create_index("ix_account_snapshots_account_id", "account_snapshots", ["tracked_account_id"])
    op.create_index("ix_follower_changes_account_id", "follower_changes", ["tracked_account_id"])
    op.create_index("ix_notifications_log_account_id", "notifications_log", ["tracked_account_id"])


def downgrade() -> None:
    op.drop_table("notifications_log")
    op.drop_table("follower_changes")
    op.drop_table("account_snapshots")
    op.drop_table("tracked_accounts")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS changetype")

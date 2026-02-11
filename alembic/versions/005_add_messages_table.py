"""Add messages table

Revision ID: 005
Revises: 004
Create Date: 2025-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JOBBOARD_ENUM = postgresql.ENUM(
    "ZIPRECRUITER", "HANDSHAKE", "WELLFOUND", "INDEED",
    "LINKEDIN", "WELCOME_TO_THE_JUNGLE", "GREENHOUSE",
    "LEVER", "OTHER", "UNKNOWN",
    name="jobboard",
    create_type=False,
)
APPLICATIONSTATUS_ENUM = postgresql.ENUM(
    "NEW", "REVIEWED", "CONTACTED", "REJECTED", "HIRED",
    name="applicationstatus",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("applicant_id", sa.Integer(), nullable=False),
        sa.Column("email_record_id", sa.Integer(), nullable=False),
        sa.Column("source", JOBBOARD_ENUM, nullable=False),
        sa.Column("message_link", sa.Text(), nullable=True),
        sa.Column("sender_email", sa.String(255), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            APPLICATIONSTATUS_ENUM,
            nullable=False,
            server_default="NEW",
        ),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["applicant_id"],
            ["applicants.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["email_record_id"],
            ["email_records.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_messages_applicant_id", "messages", ["applicant_id"])
    op.create_index("ix_messages_email_record_id", "messages", ["email_record_id"])
    op.create_index("ix_messages_source", "messages", ["source"])
    op.create_index("ix_messages_status", "messages", ["status"])

    op.create_table(
        "message_positions",
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("position_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("message_id", "position_id"),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["messages.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["position_id"],
            ["positions.id"],
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    op.drop_table("message_positions")
    op.drop_table("messages")

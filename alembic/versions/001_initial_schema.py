"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create applicants table
    op.create_table(
        "applicants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
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
        sa.UniqueConstraint("first_name", "last_name", name="uq_applicant_name"),
    )

    # Create positions table
    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
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
    )
    op.create_index("ix_positions_title", "positions", ["title"], unique=True)

    # Create email_records table
    op.create_table(
        "email_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("gmail_message_id", sa.String(255), nullable=False),
        sa.Column("gmail_thread_id", sa.String(255), nullable=False),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("sender", sa.String(255), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "processing_status",
            sa.Enum(
                "PENDING", "PROCESSED", "FAILED", "SKIPPED",
                name="emailprocessingstatus",
            ),
            nullable=False,
            default="PENDING",
        ),
        sa.Column("processing_error", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_body", sa.Text(), nullable=True),
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
    )
    op.create_index(
        "ix_email_records_gmail_message_id",
        "email_records",
        ["gmail_message_id"],
        unique=True,
    )
    op.create_index(
        "ix_email_records_gmail_thread_id",
        "email_records",
        ["gmail_thread_id"],
    )
    op.create_index(
        "ix_email_records_processing_status",
        "email_records",
        ["processing_status"],
    )

    # Create applications table
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("applicant_id", sa.Integer(), nullable=False),
        sa.Column("email_record_id", sa.Integer(), nullable=False),
        sa.Column(
            "source",
            sa.Enum(
                "ZIPRECRUITER", "HANDSHAKE", "WELLFOUND", "INDEED",
                "LINKEDIN", "WELCOME_TO_THE_JUNGLE", "GREENHOUSE",
                "LEVER", "OTHER", "UNKNOWN",
                name="jobboard",
            ),
            nullable=False,
        ),
        sa.Column("application_link", sa.Text(), nullable=True),
        sa.Column("application_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "NEW", "REVIEWED", "CONTACTED", "REJECTED", "HIRED",
                name="applicationstatus",
            ),
            nullable=False,
            default="NEW",
        ),
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
        sa.UniqueConstraint(
            "applicant_id", "source", "email_record_id",
            name="uq_application_source_email",
        ),
    )
    op.create_index("ix_applications_applicant_id", "applications", ["applicant_id"])
    op.create_index("ix_applications_email_record_id", "applications", ["email_record_id"])
    op.create_index("ix_applications_source", "applications", ["source"])
    op.create_index("ix_applications_status", "applications", ["status"])

    # Create application_positions junction table
    op.create_table(
        "application_positions",
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("position_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("application_id", "position_id"),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["position_id"],
            ["positions.id"],
            ondelete="CASCADE",
        ),
    )

    # Seed initial positions
    op.execute(
        """
        INSERT INTO positions (title, is_active, created_at, updated_at)
        VALUES
            ('UI/UX Designer', true, NOW(), NOW()),
            ('Machine Learning Engineer', true, NOW(), NOW()),
            ('Tree Expert / Arborist', true, NOW(), NOW())
        """
    )


def downgrade() -> None:
    op.drop_table("application_positions")
    op.drop_table("applications")
    op.drop_table("email_records")
    op.drop_table("positions")
    op.drop_table("applicants")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS applicationstatus")
    op.execute("DROP TYPE IF EXISTS jobboard")
    op.execute("DROP TYPE IF EXISTS emailprocessingstatus")

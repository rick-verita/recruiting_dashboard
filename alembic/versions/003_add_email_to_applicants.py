"""Add email to applicants

Revision ID: 003
Revises: 002
Create Date: 2025-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "applicants",
        sa.Column("email", sa.String(255), nullable=True),
    )
    op.create_index(op.f("ix_applicants_email"), "applicants", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_applicants_email"), table_name="applicants")
    op.drop_column("applicants", "email")

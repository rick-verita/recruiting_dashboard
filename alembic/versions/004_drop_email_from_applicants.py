"""Drop email from applicants

Revision ID: 004
Revises: 003
Create Date: 2025-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f("ix_applicants_email"), table_name="applicants")
    op.drop_column("applicants", "email")


def downgrade() -> None:
    op.add_column(
        "applicants",
        sa.Column("email", sa.String(255), nullable=True),
    )
    op.create_index(op.f("ix_applicants_email"), "applicants", ["email"], unique=False)

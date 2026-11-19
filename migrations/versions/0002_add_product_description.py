"""add product description

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-19 10:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    # SQLite >= 3.35 поддерживает ALTER TABLE ... DROP COLUMN
    op.drop_column("products", "description")

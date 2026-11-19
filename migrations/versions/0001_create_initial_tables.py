"""create initial tables

Revision ID: 0001
Revises:
Create Date: 2026-11-19 10:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("role IN ('director', 'manager', 'analyst', 'admin')", name="ck_users_role"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_products_price"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "metric_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("metric_name", sa.String(length=50), nullable=False),
        sa.Column("formula", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("metric_name"),
    )
    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_date", sa.Date(), nullable=False),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column("revenue", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("orders_count", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=False),
        sa.CheckConstraint("revenue >= 0", name="ck_sales_revenue"),
        sa.CheckConstraint("cost >= 0", name="ck_sales_cost"),
        sa.CheckConstraint("orders_count >= 1", name="ck_sales_orders_count"),
        sa.ForeignKeyConstraint(["manager_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_sales_month", "sales", ["month"], unique=False)
    op.create_index("idx_sales_manager_id", "sales", ["manager_id"], unique=False)
    op.create_index("idx_sales_product_id", "sales", ["product_id"], unique=False)
    op.create_table(
        "kpi",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(length=7), nullable=False),
        sa.Column("metric_name", sa.String(length=50), nullable=False),
        sa.Column("value", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("calculated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["metric_name"], ["metric_settings.metric_name"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("period", "metric_name", name="uq_kpi_period_metric"),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_type", sa.String(length=30), nullable=False),
        sa.Column("period", sa.String(length=7), nullable=False),
        sa.Column("file_path", sa.String(length=255), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("kpi")
    op.drop_index("idx_sales_product_id", table_name="sales")
    op.drop_index("idx_sales_manager_id", table_name="sales")
    op.drop_index("idx_sales_month", table_name="sales")
    op.drop_table("sales")
    op.drop_table("metric_settings")
    op.drop_table("products")
    op.drop_table("users")

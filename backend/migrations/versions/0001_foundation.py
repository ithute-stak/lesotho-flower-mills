"""Initial customer and catalogue foundations.

Revision ID: 0001_foundation
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS crm")
    op.execute("CREATE SCHEMA IF NOT EXISTS catalog")
    op.create_table(
        "customers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("customer_number", sa.String(40), nullable=False, unique=True),
        sa.Column("customer_type", sa.String(16), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("phone_e164", sa.String(20), nullable=True),
        sa.Column("verification_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("customer_type IN ('individual', 'business')", name="ck_customer_type"),
        schema="crm",
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("sku", sa.String(64), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("stock_unit", sa.String(32), nullable=False, server_default="bag"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        schema="catalog",
    )


def downgrade() -> None:
    op.drop_table("products", schema="catalog")
    op.drop_table("customers", schema="crm")
    op.execute("DROP SCHEMA IF EXISTS catalog")
    op.execute("DROP SCHEMA IF EXISTS crm")

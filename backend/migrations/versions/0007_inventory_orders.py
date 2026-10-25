"""Stock balances, reservations and controlled sales orders.

Revision ID: 0007_inventory_orders
Revises: 0006_customer_prices
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_inventory_orders"
down_revision = "0006_customer_prices"
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS inventory")
    op.create_table("warehouses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(40), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        schema="inventory")
    op.create_table("stock_balances",
        sa.Column("warehouse_id", sa.Uuid(), sa.ForeignKey("inventory.warehouses.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("catalog.products.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("on_hand", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reserved", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("on_hand >= 0 AND reserved >= 0 AND reserved <= on_hand", name="ck_stock_available"),
        schema="inventory")
    op.create_table("stock_reservations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("quotation_item_id", sa.Uuid(), sa.ForeignKey("sales.quotation_items.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("warehouse_id", sa.Uuid(), sa.ForeignKey("inventory.warehouses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("catalog.products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_positive_reservation"),
        sa.CheckConstraint("status IN ('active','released','consumed')", name="ck_reservation_state"),
        schema="inventory")
    op.create_table("sales_orders",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("order_number", sa.String(50), nullable=False, unique=True),
        sa.Column("quotation_id", sa.Uuid(), sa.ForeignKey("sales.quotations.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("customer_id", sa.Uuid(), sa.ForeignKey("crm.customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("warehouse_id", sa.Uuid(), sa.ForeignKey("inventory.warehouses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending_payment"),
        sa.Column("subtotal", sa.Numeric(18,2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('pending_payment','pending_credit_approval','confirmed','cancelled')", name="ck_sales_order_state"),
        schema="sales")

def downgrade():
    op.drop_table("sales_orders", schema="sales")
    op.drop_table("stock_reservations", schema="inventory")
    op.drop_table("stock_balances", schema="inventory")
    op.drop_table("warehouses", schema="inventory")
    op.execute("DROP SCHEMA IF EXISTS inventory")

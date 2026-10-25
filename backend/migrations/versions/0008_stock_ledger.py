"""Immutable stock movement journal and unique operation keys.

Revision ID: 0008_stock_ledger
Revises: 0007_inventory_orders
"""
from alembic import op
import sqlalchemy as sa
revision="0008_stock_ledger"
down_revision="0007_inventory_orders"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("stock_movements",
        sa.Column("id",sa.Uuid(),primary_key=True),
        sa.Column("operation_key",sa.String(128),nullable=False,unique=True),
        sa.Column("warehouse_id",sa.Uuid(),sa.ForeignKey("inventory.warehouses.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("product_id",sa.Uuid(),sa.ForeignKey("catalog.products.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("delta",sa.Integer(),nullable=False),
        sa.Column("movement_type",sa.String(24),nullable=False),
        sa.Column("reference",sa.String(160),nullable=False),
        sa.Column("actor_id",sa.String(255),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
        sa.CheckConstraint("delta <> 0",name="ck_nonzero_movement"),
        sa.CheckConstraint("movement_type IN ('receipt','adjustment','transfer_in','transfer_out')",name="ck_movement_type"),
        schema="inventory")
    op.create_table("stock_operations",
        sa.Column("id",sa.Uuid(),primary_key=True),
        sa.Column("operation_key",sa.String(128),nullable=False,unique=True),
        sa.Column("operation_type",sa.String(32),nullable=False),
        sa.Column("actor_id",sa.String(255),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
        schema="inventory")

def downgrade():
    op.drop_table("stock_movements",schema="inventory")
    op.drop_table("stock_operations",schema="inventory")

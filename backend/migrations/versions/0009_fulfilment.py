"""Picking and loading records; dispatch intentionally blocked until payment verification.

Revision ID: 0009_fulfilment
Revises: 0008_stock_ledger
"""
from alembic import op
import sqlalchemy as sa
revision="0009_fulfilment"
down_revision="0008_stock_ledger"
branch_labels=None
depends_on=None

def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS fulfilment")
    op.create_table("pick_lists",
      sa.Column("id",sa.Uuid(),primary_key=True),
      sa.Column("sales_order_id",sa.Uuid(),sa.ForeignKey("sales.sales_orders.id",ondelete="RESTRICT"),nullable=False,unique=True),
      sa.Column("status",sa.String(24),nullable=False,server_default="pending"),
      sa.Column("created_by",sa.String(255),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
      sa.CheckConstraint("status IN ('pending','picked','cancelled')",name="ck_pick_status"),
      schema="fulfilment")
    op.create_table("pick_items",
      sa.Column("id",sa.Uuid(),primary_key=True),
      sa.Column("pick_list_id",sa.Uuid(),sa.ForeignKey("fulfilment.pick_lists.id",ondelete="RESTRICT"),nullable=False),
      sa.Column("quotation_item_id",sa.Uuid(),sa.ForeignKey("sales.quotation_items.id",ondelete="RESTRICT"),nullable=False,unique=True),
      sa.Column("required_qty",sa.Integer(),nullable=False),
      sa.Column("picked_qty",sa.Integer(),nullable=False,server_default="0"),
      sa.CheckConstraint("required_qty>0 AND picked_qty>=0 AND picked_qty<=required_qty",name="ck_picked_qty"),
      schema="fulfilment")
    op.create_table("loading_manifests",
      sa.Column("id",sa.Uuid(),primary_key=True),
      sa.Column("pick_list_id",sa.Uuid(),sa.ForeignKey("fulfilment.pick_lists.id",ondelete="RESTRICT"),nullable=False,unique=True),
      sa.Column("vehicle_registration",sa.String(40),nullable=False),
      sa.Column("driver_name",sa.String(150),nullable=False),
      sa.Column("status",sa.String(24),nullable=False,server_default="loading"),
      sa.Column("verified_by",sa.String(255)),
      sa.Column("verified_at",sa.DateTime(timezone=True)),
      sa.CheckConstraint("status IN ('loading','verified')",name="ck_manifest_status"),
      schema="fulfilment")
    op.create_table("loading_items",
      sa.Column("id",sa.Uuid(),primary_key=True),
      sa.Column("manifest_id",sa.Uuid(),sa.ForeignKey("fulfilment.loading_manifests.id",ondelete="RESTRICT"),nullable=False),
      sa.Column("pick_item_id",sa.Uuid(),sa.ForeignKey("fulfilment.pick_items.id",ondelete="RESTRICT"),nullable=False,unique=True),
      sa.Column("loaded_qty",sa.Integer(),nullable=False),
      sa.CheckConstraint("loaded_qty>0",name="ck_loaded_qty"),
      schema="fulfilment")

def downgrade():
    op.drop_table("loading_items",schema="fulfilment")
    op.drop_table("loading_manifests",schema="fulfilment")
    op.drop_table("pick_items",schema="fulfilment")
    op.drop_table("pick_lists",schema="fulfilment")
    op.execute("DROP SCHEMA IF EXISTS fulfilment")

"""Versioned commercial breakdown for orders; disabled until approved.

Revision ID: 0015_order_totals
Revises: 0014_checkout_sessions
"""
from alembic import op
import sqlalchemy as sa
revision="0015_order_totals"
down_revision="0014_checkout_sessions"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("order_totals",
  sa.Column("sales_order_id",sa.Uuid(),sa.ForeignKey("sales.sales_orders.id",ondelete="RESTRICT"),primary_key=True),
  sa.Column("subtotal",sa.Numeric(18,2),nullable=False),
  sa.Column("discount",sa.Numeric(18,2),nullable=False,server_default="0"),
  sa.Column("delivery_fee",sa.Numeric(18,2),nullable=False,server_default="0"),
  sa.Column("tax_rate_bps",sa.Integer(),nullable=False),
  sa.Column("taxable_base",sa.Numeric(18,2),nullable=False),
  sa.Column("tax_amount",sa.Numeric(18,2),nullable=False),
  sa.Column("total",sa.Numeric(18,2),nullable=False),
  sa.Column("currency",sa.String(3),nullable=False,server_default="LSL"),
  sa.Column("policy_reference",sa.String(120),nullable=False),
  sa.Column("approved_by",sa.String(255)),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("subtotal>=0 AND discount>=0 AND delivery_fee>=0 AND tax_amount>=0 AND total>=0",name="ck_order_total_nonnegative"),
  sa.CheckConstraint("tax_rate_bps>=0 AND tax_rate_bps<=10000",name="ck_order_tax_rate"),
  schema="finance")
def downgrade():
 op.drop_table("order_totals",schema="finance")

"""Durable checkout initiation journal.

Revision ID: 0020_checkout_recovery
Revises: 0019_total_audit
"""
from alembic import op
import sqlalchemy as sa
revision="0020_checkout_recovery"
down_revision="0019_total_audit"
branch_labels=None
depends_on=None

def upgrade():
 op.create_table("checkout_attempts",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("sales_order_id",sa.Uuid(),sa.ForeignKey("sales.sales_orders.id",ondelete="RESTRICT"),nullable=False,unique=True),
  sa.Column("idempotency_key",sa.String(128),nullable=False,unique=True),
  sa.Column("state",sa.String(24),nullable=False,server_default="initiating"),
  sa.Column("provider_session_id",sa.String(128),unique=True),
  sa.Column("amount",sa.Numeric(18,2),nullable=False),
  sa.Column("currency",sa.String(3),nullable=False,server_default="LSL"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.CheckConstraint("state IN ('initiating','created','reconciliation_required')",name="ck_checkout_attempt_state"),
  sa.CheckConstraint("amount > 0",name="ck_checkout_attempt_amount"),
  schema="finance")

def downgrade():
 op.drop_table("checkout_attempts",schema="finance")

"""Order-linked IthutePay checkout references.

Revision ID: 0014_checkout_sessions
Revises: 0013_delivery_disputes
"""
from alembic import op
import sqlalchemy as sa
revision="0014_checkout_sessions"
down_revision="0013_delivery_disputes"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("checkout_sessions",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("sales_order_id",sa.Uuid(),sa.ForeignKey("sales.sales_orders.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("provider_session_id",sa.String(128),nullable=False,unique=True),
  sa.Column("idempotency_key",sa.String(128),nullable=False,unique=True),
  sa.Column("amount",sa.Numeric(18,2),nullable=False),
  sa.Column("currency",sa.String(3),nullable=False,server_default="LSL"),
  sa.Column("state",sa.String(30),nullable=False,server_default="created"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.Column("last_checked_at",sa.DateTime(timezone=True)),
  sa.CheckConstraint("amount>0",name="ck_checkout_positive"),
  schema="finance")
 op.create_index("ix_checkout_sessions_order","checkout_sessions",["sales_order_id"],schema="finance")
def downgrade():
 op.drop_index("ix_checkout_sessions_order",table_name="checkout_sessions",schema="finance")
 op.drop_table("checkout_sessions",schema="finance")

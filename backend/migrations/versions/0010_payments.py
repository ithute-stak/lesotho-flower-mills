"""Payment verification ledger and credit approvals.

Revision ID: 0010_payments
Revises: 0009_fulfilment
"""
from alembic import op
import sqlalchemy as sa
revision="0010_payments"
down_revision="0009_fulfilment"
branch_labels=None
depends_on=None

def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS finance")
    op.create_table("payment_transactions",
      sa.Column("id",sa.Uuid(),primary_key=True),
      sa.Column("sales_order_id",sa.Uuid(),sa.ForeignKey("sales.sales_orders.id",ondelete="RESTRICT"),nullable=False),
      sa.Column("provider",sa.String(60),nullable=False),
      sa.Column("provider_reference",sa.String(180),nullable=False),
      sa.Column("amount",sa.Numeric(18,2),nullable=False),
      sa.Column("currency",sa.String(3),nullable=False,server_default="LSL"),
      sa.Column("verification_status",sa.String(24),nullable=False,server_default="pending"),
      sa.Column("evidence_reference",sa.String(255)),
      sa.Column("verified_at",sa.DateTime(timezone=True)),
      sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
      sa.CheckConstraint("amount > 0",name="ck_payment_amount_positive"),
      sa.CheckConstraint("verification_status IN ('pending','verified','rejected','reversed')",name="ck_payment_verification_status"),
      sa.UniqueConstraint("provider","provider_reference",name="uq_provider_payment_reference"),
      schema="finance")
    op.create_table("order_authorisations",
      sa.Column("id",sa.Uuid(),primary_key=True),
      sa.Column("sales_order_id",sa.Uuid(),sa.ForeignKey("sales.sales_orders.id",ondelete="RESTRICT"),nullable=False,unique=True),
      sa.Column("authorisation_type",sa.String(20),nullable=False),
      sa.Column("approved_by",sa.String(255),nullable=False),
      sa.Column("evidence_reference",sa.String(255),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
      sa.CheckConstraint("authorisation_type IN ('payment','credit')",name="ck_authorisation_type"),
      schema="finance")

def downgrade():
    op.drop_table("order_authorisations",schema="finance")
    op.drop_table("payment_transactions",schema="finance")
    op.execute("DROP SCHEMA IF EXISTS finance")

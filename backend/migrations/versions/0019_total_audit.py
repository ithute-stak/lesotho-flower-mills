"""Immutable audit events for financial total review.

Revision ID: 0019_total_audit
Revises: 0018_financial_policies
"""
from alembic import op
import sqlalchemy as sa
revision="0019_total_audit"
down_revision="0018_financial_policies"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("total_review_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("sales_order_id",sa.Uuid(),sa.ForeignKey("sales.sales_orders.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("actor_subject",sa.String(255),nullable=False),
  sa.Column("action",sa.String(32),nullable=False),
  sa.Column("total_amount",sa.Numeric(18,2),nullable=False),
  sa.Column("policy_reference",sa.String(120),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.CheckConstraint("action IN ('approved','rejected')",name="ck_total_review_action"),
  schema="finance")
 op.execute("""CREATE OR REPLACE FUNCTION finance.prevent_total_audit_mutation()
 RETURNS trigger LANGUAGE plpgsql AS $$
 BEGIN RAISE EXCEPTION 'Financial audit events cannot be modified'; END $$""")
 op.execute("""CREATE TRIGGER trg_total_audit_immutable BEFORE UPDATE OR DELETE
 ON finance.total_review_events FOR EACH ROW EXECUTE FUNCTION finance.prevent_total_audit_mutation()""")
def downgrade():
 op.execute("DROP TRIGGER IF EXISTS trg_total_audit_immutable ON finance.total_review_events")
 op.execute("DROP FUNCTION IF EXISTS finance.prevent_total_audit_mutation()")
 op.drop_table("total_review_events",schema="finance")

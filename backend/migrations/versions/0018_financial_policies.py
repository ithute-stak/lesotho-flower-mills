"""Versioned financial policies and maker-checker approval.

Revision ID: 0018_financial_policies
Revises: 0017_total_approval
"""
from alembic import op
import sqlalchemy as sa
revision="0018_financial_policies"
down_revision="0017_total_approval"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("financial_policies",
   sa.Column("id",sa.Uuid(),primary_key=True),
   sa.Column("code",sa.String(80),nullable=False),
   sa.Column("version",sa.Integer(),nullable=False),
   sa.Column("tax_rate_bps",sa.Integer(),nullable=False),
   sa.Column("delivery_taxable",sa.Boolean(),nullable=False,server_default=sa.false()),
   sa.Column("max_discount_bps",sa.Integer(),nullable=False,server_default="0"),
   sa.Column("status",sa.String(20),nullable=False,server_default="draft"),
   sa.Column("created_by",sa.String(255),nullable=False),
   sa.Column("approved_by",sa.String(255)),
   sa.Column("effective_from",sa.DateTime(timezone=True)),
   sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
   sa.CheckConstraint("tax_rate_bps BETWEEN 0 AND 10000 AND max_discount_bps BETWEEN 0 AND 10000",name="ck_financial_policy_rates"),
   sa.CheckConstraint("status IN ('draft','approved','rejected')",name="ck_financial_policy_status"),
   sa.CheckConstraint("approved_by IS NULL OR approved_by <> created_by",name="ck_financial_policy_separation"),
   sa.UniqueConstraint("code","version",name="uq_financial_policy_version"),
   schema="finance")
 op.execute("""CREATE OR REPLACE FUNCTION finance.guard_approved_policy()
 RETURNS trigger LANGUAGE plpgsql AS $$
 BEGIN
 IF OLD.status='approved' THEN RAISE EXCEPTION 'Approved policy is immutable'; END IF;
 RETURN NEW;
 END $$""")
 op.execute("""CREATE TRIGGER trg_guard_approved_policy BEFORE UPDATE OR DELETE ON finance.financial_policies
 FOR EACH ROW EXECUTE FUNCTION finance.guard_approved_policy()""")
def downgrade():
 op.execute("DROP TRIGGER IF EXISTS trg_guard_approved_policy ON finance.financial_policies")
 op.execute("DROP FUNCTION IF EXISTS finance.guard_approved_policy()")
 op.drop_table("financial_policies",schema="finance")

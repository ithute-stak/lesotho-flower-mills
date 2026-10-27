"""Referral attribution planning; no reward or credit issuance."""
from alembic import op
import sqlalchemy as sa
revision="0043_referral_plans"
down_revision="0042_customer_engagement"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("referral_plans",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("referrer_customer_id",sa.Uuid(),sa.ForeignKey("crm.customers.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("referred_customer_id",sa.Uuid(),sa.ForeignKey("crm.customers.id",ondelete="RESTRICT"),nullable=False,unique=True),
  sa.Column("status",sa.String(16),nullable=False,server_default="draft"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("referrer_customer_id <> referred_customer_id",name="ck_referral_distinct_customers"),
  sa.CheckConstraint("status='draft'",name="ck_referral_draft_only"),
  schema="marketing")
def downgrade():
 op.drop_table("referral_plans",schema="marketing")

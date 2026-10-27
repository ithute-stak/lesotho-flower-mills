"""Draft budget authorization for campaigns; checkout spending remains disabled."""
from alembic import op
import sqlalchemy as sa
revision="0038_campaign_budgets"
down_revision="0037_coupon_events"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("campaign_budgets",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("campaign_id",sa.Uuid(),sa.ForeignKey("marketing.campaigns.id",ondelete="RESTRICT"),nullable=False,unique=True),
  sa.Column("limit_amount",sa.Numeric(18,2),nullable=False),
  sa.Column("currency",sa.String(3),nullable=False,server_default="LSL"),
  sa.Column("status",sa.String(16),nullable=False,server_default="draft"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("approved_by",sa.String(255)),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.CheckConstraint("limit_amount > 0",name="ck_campaign_budget_positive"),
  sa.CheckConstraint("currency='LSL'",name="ck_campaign_budget_currency"),
  sa.CheckConstraint("status IN ('draft','approved')",name="ck_campaign_budget_status"),
  schema="marketing")
 op.create_table("campaign_budget_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("budget_id",sa.Uuid(),sa.ForeignKey("marketing.campaign_budgets.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("actor_subject",sa.String(255),nullable=False),
  sa.Column("action",sa.String(20),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.CheckConstraint("action IN ('created','approved')",name="ck_campaign_budget_action"),
  schema="marketing")
 op.execute("""CREATE FUNCTION marketing.reject_budget_event_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
 BEGIN RAISE EXCEPTION 'Budget audit history is immutable'; END $$""")
 op.execute("""CREATE TRIGGER budget_events_immutable BEFORE UPDATE OR DELETE ON marketing.campaign_budget_events
 FOR EACH ROW EXECUTE FUNCTION marketing.reject_budget_event_mutation()""")
def downgrade():
 op.execute("DROP TRIGGER budget_events_immutable ON marketing.campaign_budget_events")
 op.execute("DROP FUNCTION marketing.reject_budget_event_mutation()")
 op.drop_table("campaign_budget_events",schema="marketing")
 op.drop_table("campaign_budgets",schema="marketing")

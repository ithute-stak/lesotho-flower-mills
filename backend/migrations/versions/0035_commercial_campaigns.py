"""Draft-only campaigns with immutable independent-approval audit."""
from alembic import op
import sqlalchemy as sa

revision="0035_commercial_campaigns"
down_revision="0034_order_cancellation_audit"
branch_labels=None
depends_on=None

def upgrade():
 op.execute("CREATE SCHEMA IF NOT EXISTS marketing")
 op.create_table("campaigns",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("code",sa.String(80),nullable=False,unique=True),
  sa.Column("discount_bps",sa.Integer(),nullable=False),
  sa.Column("minimum_subtotal",sa.Numeric(18,2),nullable=False),
  sa.Column("maximum_discount",sa.Numeric(18,2),nullable=True),
  sa.Column("audience",sa.String(16),nullable=False),
  sa.Column("starts_at",sa.DateTime(timezone=True),nullable=False),
  sa.Column("ends_at",sa.DateTime(timezone=True),nullable=False),
  sa.Column("status",sa.String(16),nullable=False,server_default="draft"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("approved_by",sa.String(255)),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("discount_bps >= 0 AND discount_bps <= 10000",name="ck_campaign_discount"),
  sa.CheckConstraint("minimum_subtotal >= 0 AND (maximum_discount IS NULL OR maximum_discount >= 0)",name="ck_campaign_amounts"),
  sa.CheckConstraint("ends_at > starts_at",name="ck_campaign_window"),
  sa.CheckConstraint("audience IN ('public','business')",name="ck_campaign_audience"),
  sa.CheckConstraint("status IN ('draft','approved','disabled')",name="ck_campaign_status"),
  schema="marketing")
 op.create_table("campaign_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("campaign_id",sa.Uuid(),sa.ForeignKey("marketing.campaigns.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("actor_subject",sa.String(255),nullable=False),
  sa.Column("action",sa.String(32),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  schema="marketing")
 op.execute("""CREATE FUNCTION marketing.reject_campaign_event_mutation()
 RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
 RAISE EXCEPTION 'Campaign audit history is immutable';
 END $$""")
 op.execute("""CREATE TRIGGER campaign_events_immutable BEFORE UPDATE OR DELETE
 ON marketing.campaign_events FOR EACH ROW
 EXECUTE FUNCTION marketing.reject_campaign_event_mutation()""")

def downgrade():
 op.execute("DROP TRIGGER campaign_events_immutable ON marketing.campaign_events")
 op.execute("DROP FUNCTION marketing.reject_campaign_event_mutation()")
 op.drop_table("campaign_events",schema="marketing")
 op.drop_table("campaigns",schema="marketing")

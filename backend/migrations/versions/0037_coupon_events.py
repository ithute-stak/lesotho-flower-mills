"""Immutable administrative coupon audit log; no redemption writes."""
from alembic import op
import sqlalchemy as sa
revision="0037_coupon_events"
down_revision="0036_campaign_coupons"
branch_labels=None
depends_on=None

def upgrade():
 op.create_table("coupon_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("coupon_id",sa.Uuid(),sa.ForeignKey("marketing.coupons.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("actor_subject",sa.String(255),nullable=False),
  sa.Column("action",sa.String(32),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("action IN ('created','disabled')",name="ck_coupon_event_action"),
  schema="marketing")
 op.create_index("ix_coupon_events_coupon","coupon_events",["coupon_id"],schema="marketing")
 op.execute("""CREATE FUNCTION marketing.reject_coupon_event_mutation()
 RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
 RAISE EXCEPTION 'Coupon audit history is immutable';
 END $$""")
 op.execute("""CREATE TRIGGER coupon_events_immutable BEFORE UPDATE OR DELETE
 ON marketing.coupon_events FOR EACH ROW
 EXECUTE FUNCTION marketing.reject_coupon_event_mutation()""")

def downgrade():
 op.execute("DROP TRIGGER coupon_events_immutable ON marketing.coupon_events")
 op.execute("DROP FUNCTION marketing.reject_coupon_event_mutation()")
 op.drop_index("ix_coupon_events_coupon",table_name="coupon_events",schema="marketing")
 op.drop_table("coupon_events",schema="marketing")

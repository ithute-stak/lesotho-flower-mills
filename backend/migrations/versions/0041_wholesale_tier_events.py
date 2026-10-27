"""Append-only audit trail for wholesale discount tiers."""
from alembic import op
import sqlalchemy as sa
revision="0041_wholesale_tier_events"
down_revision="0040_wholesale_discount_tiers"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("wholesale_tier_events",
 sa.Column("id",sa.Uuid(),primary_key=True),
 sa.Column("tier_id",sa.Uuid(),sa.ForeignKey("marketing.wholesale_discount_tiers.id",ondelete="RESTRICT"),nullable=False),
 sa.Column("actor_subject",sa.String(255),nullable=False),
 sa.Column("action",sa.String(20),nullable=False),
 sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
 sa.CheckConstraint("action IN ('created','approved','disabled')",name="ck_wholesale_tier_event_action"),
 schema="marketing")
 op.create_index("ix_wholesale_tier_events_tier","wholesale_tier_events",["tier_id"],schema="marketing")
 op.execute("""CREATE FUNCTION marketing.reject_wholesale_tier_event_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
 BEGIN RAISE EXCEPTION 'Wholesale tier audit history is immutable'; END $$""")
 op.execute("""CREATE TRIGGER wholesale_tier_events_immutable BEFORE UPDATE OR DELETE
 ON marketing.wholesale_tier_events FOR EACH ROW EXECUTE FUNCTION marketing.reject_wholesale_tier_event_mutation()""")
def downgrade():
 op.execute("DROP TRIGGER wholesale_tier_events_immutable ON marketing.wholesale_tier_events")
 op.execute("DROP FUNCTION marketing.reject_wholesale_tier_event_mutation()")
 op.drop_index("ix_wholesale_tier_events_tier",table_name="wholesale_tier_events",schema="marketing")
 op.drop_table("wholesale_tier_events",schema="marketing")

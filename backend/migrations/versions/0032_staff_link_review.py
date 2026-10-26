"""Maker-checker central staff link review and immutable event history."""
from alembic import op
import sqlalchemy as sa
revision="0032_staff_link_review"
down_revision="0031_central_staff_links"
branch_labels=None
depends_on=None
def upgrade():
 op.add_column("central_staff_links",sa.Column("requested_by",sa.String(255)),schema="identity")
 op.create_table("central_staff_link_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("link_id",sa.Uuid(),sa.ForeignKey("identity.central_staff_links.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("action",sa.String(20),nullable=False),
  sa.Column("actor",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("action IN ('requested','verified','revoked')",name="ck_staff_link_action"),schema="identity")
 op.execute("""CREATE OR REPLACE FUNCTION identity.reject_staff_link_event_mutation()
 RETURNS trigger LANGUAGE plpgsql AS $$
 BEGIN RAISE EXCEPTION 'Staff link history is immutable'; END $$""")
 op.execute("""CREATE TRIGGER staff_link_events_immutable BEFORE UPDATE OR DELETE
 ON identity.central_staff_link_events FOR EACH ROW EXECUTE FUNCTION identity.reject_staff_link_event_mutation()""")
def downgrade():
 op.execute("DROP TRIGGER staff_link_events_immutable ON identity.central_staff_link_events")
 op.execute("DROP FUNCTION identity.reject_staff_link_event_mutation()")
 op.drop_table("central_staff_link_events",schema="identity")
 op.drop_column("central_staff_links","requested_by",schema="identity")

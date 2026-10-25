"""Append-only email incident investigation notes. Revision: 0026_delivery_incidents."""
from alembic import op
import sqlalchemy as sa
revision="0026_delivery_incidents"
down_revision="0025_alert_delivery"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("alert_delivery_incidents",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("outbox_id",sa.Uuid(),sa.ForeignKey("finance.alert_outbox.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("actor",sa.String(255),nullable=False),
  sa.Column("disposition",sa.String(24),nullable=False),
  sa.Column("note",sa.Text(),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("disposition IN ('investigating','confirmed_sent','delivery_unverified')",name="ck_email_incident_disposition"),
  schema="finance")
 op.execute("""CREATE OR REPLACE FUNCTION finance.prevent_alert_incident_mutation()
 RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
 RAISE EXCEPTION 'Notification incident audit records cannot be changed'; END $$""")
 op.execute("""CREATE TRIGGER trg_alert_incident_immutable BEFORE UPDATE OR DELETE
 ON finance.alert_delivery_incidents FOR EACH ROW EXECUTE FUNCTION finance.prevent_alert_incident_mutation()""")
def downgrade():
 op.execute("DROP TRIGGER IF EXISTS trg_alert_incident_immutable ON finance.alert_delivery_incidents")
 op.execute("DROP FUNCTION IF EXISTS finance.prevent_alert_incident_mutation()")
 op.drop_table("alert_delivery_incidents",schema="finance")

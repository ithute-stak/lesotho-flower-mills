"""Append-only cancellation audit records."""
from alembic import op
import sqlalchemy as sa
revision="0034_order_cancellation_audit"
down_revision="0033_staff_identity_attestation"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("order_cancellation_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("order_id",sa.Uuid(),sa.ForeignKey("sales.sales_orders.id",ondelete="RESTRICT"),nullable=False,unique=True),
  sa.Column("actor_subject",sa.String(255),nullable=False),
  sa.Column("released_count",sa.Integer(),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.CheckConstraint("released_count >= 0",name="ck_cancel_released_count"),
  schema="sales")
 op.execute("""CREATE OR REPLACE FUNCTION sales.reject_cancellation_event_mutation()
 RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
 RAISE EXCEPTION 'Cancellation audit history is immutable';
 END $$""")
 op.execute("""CREATE TRIGGER cancellation_events_immutable BEFORE UPDATE OR DELETE
 ON sales.order_cancellation_events FOR EACH ROW
 EXECUTE FUNCTION sales.reject_cancellation_event_mutation()""")
def downgrade():
 op.execute("DROP TRIGGER cancellation_events_immutable ON sales.order_cancellation_events")
 op.execute("DROP FUNCTION sales.reject_cancellation_event_mutation()")
 op.drop_table("order_cancellation_events",schema="sales")

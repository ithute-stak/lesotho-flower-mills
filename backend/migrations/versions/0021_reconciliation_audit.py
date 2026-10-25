"""Immutable checkout reconciliation observations and review queue.

Revision ID: 0021_reconciliation_audit
Revises: 0020_checkout_recovery
"""
from alembic import op
import sqlalchemy as sa
revision="0021_reconciliation_audit"
down_revision="0020_checkout_recovery"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("reconciliation_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("checkout_attempt_id",sa.Uuid(),sa.ForeignKey("finance.checkout_attempts.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("outcome",sa.String(30),nullable=False),
  sa.Column("remote_status",sa.String(30)),
  sa.Column("actor",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("outcome IN ('observed','mismatch','unreachable','needs_review')",name="ck_recon_outcome"),
  schema="finance")
 op.create_index("ix_recon_events_attempt","reconciliation_events",["checkout_attempt_id","created_at"],schema="finance")
 op.execute("""CREATE OR REPLACE FUNCTION finance.prevent_reconciliation_event_mutation()
 RETURNS trigger LANGUAGE plpgsql AS $$
 BEGIN RAISE EXCEPTION 'Reconciliation events are append only'; END $$""")
 op.execute("""CREATE TRIGGER trg_recon_events_immutable BEFORE UPDATE OR DELETE
 ON finance.reconciliation_events FOR EACH ROW EXECUTE FUNCTION finance.prevent_reconciliation_event_mutation()""")
def downgrade():
 op.execute("DROP TRIGGER IF EXISTS trg_recon_events_immutable ON finance.reconciliation_events")
 op.execute("DROP FUNCTION IF EXISTS finance.prevent_reconciliation_event_mutation()")
 op.drop_index("ix_recon_events_attempt",table_name="reconciliation_events",schema="finance")
 op.drop_table("reconciliation_events",schema="finance")

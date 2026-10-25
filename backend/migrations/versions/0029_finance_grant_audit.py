"""Append-only finance grant events. Revision ID: 0029_finance_grant_audit."""
from alembic import op
import sqlalchemy as sa
revision="0029_finance_grant_audit"
down_revision="0028_finance_grant_requests"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("finance_grant_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("request_id",sa.Uuid(),sa.ForeignKey("finance.finance_grant_requests.id",ondelete="RESTRICT")),
  sa.Column("grant_id",sa.Uuid(),sa.ForeignKey("finance.finance_role_grants.id",ondelete="RESTRICT")),
  sa.Column("subject",sa.String(255),nullable=False),
  sa.Column("role",sa.String(32),nullable=False),
  sa.Column("action",sa.String(24),nullable=False),
  sa.Column("actor",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("action IN ('requested','approved','revoked')",name="ck_grant_audit_action"),
  schema="finance")
 op.create_index("ix_grant_events_subject","finance_grant_events",["subject","created_at"],schema="finance")
 op.execute("""CREATE OR REPLACE FUNCTION finance.prevent_finance_grant_event_mutation()
 RETURNS trigger LANGUAGE plpgsql AS $$
 BEGIN RAISE EXCEPTION 'Finance grant audit events are immutable'; END $$""")
 op.execute("""CREATE TRIGGER trg_finance_grant_events_immutable BEFORE UPDATE OR DELETE
 ON finance.finance_grant_events FOR EACH ROW EXECUTE FUNCTION finance.prevent_finance_grant_event_mutation()""")
def downgrade():
 op.execute("DROP TRIGGER IF EXISTS trg_finance_grant_events_immutable ON finance.finance_grant_events")
 op.execute("DROP FUNCTION IF EXISTS finance.prevent_finance_grant_event_mutation()")
 op.drop_index("ix_grant_events_subject",table_name="finance_grant_events",schema="finance")
 op.drop_table("finance_grant_events",schema="finance")

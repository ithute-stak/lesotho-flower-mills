"""Persist one-shot reconciliation runs. Revision: 0022_reconciliation_runs."""
from alembic import op
import sqlalchemy as sa
revision="0022_reconciliation_runs"
down_revision="0021_reconciliation_audit"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("reconciliation_runs",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("started_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.Column("finished_at",sa.DateTime(timezone=True)),
  sa.Column("status",sa.String(24),nullable=False),
  sa.Column("checked",sa.Integer(),nullable=False,server_default="0"),
  sa.Column("updated",sa.Integer(),nullable=False,server_default="0"),
  sa.CheckConstraint("status IN ('running','completed','failed','skipped')",name="ck_recon_run_status"),
  schema="finance")
 op.create_index("ix_reconciliation_runs_started","reconciliation_runs",["started_at"],schema="finance")
def downgrade():
 op.drop_index("ix_reconciliation_runs_started",table_name="reconciliation_runs",schema="finance")
 op.drop_table("reconciliation_runs",schema="finance")

"""Financial operational alert records.

Revision ID: 0023_finance_alerts
Revises: 0022_reconciliation_runs
"""
from alembic import op
import sqlalchemy as sa
revision="0023_finance_alerts"
down_revision="0022_reconciliation_runs"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("operational_alerts",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("code",sa.String(64),nullable=False),
  sa.Column("dedupe_key",sa.String(140),nullable=False,unique=True),
  sa.Column("severity",sa.String(12),nullable=False),
  sa.Column("details",sa.Text(),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("severity IN ('warning','critical')",name="ck_finance_alert_severity"),
  schema="finance")
def downgrade():
 op.drop_table("operational_alerts",schema="finance")

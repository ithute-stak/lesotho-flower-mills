"""Durable notification outbox. Revision ID: 0024_alert_outbox."""
from alembic import op
import sqlalchemy as sa
revision="0024_alert_outbox"
down_revision="0023_finance_alerts"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("alert_outbox",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("alert_id",sa.Uuid(),sa.ForeignKey("finance.operational_alerts.id",ondelete="RESTRICT"),nullable=False,unique=True),
  sa.Column("channel",sa.String(16),nullable=False,server_default="email"),
  sa.Column("state",sa.String(20),nullable=False,server_default="pending"),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.Column("processed_at",sa.DateTime(timezone=True)),
  sa.CheckConstraint("channel IN ('email')",name="ck_alert_channel"),
  sa.CheckConstraint("state IN ('pending','sent','failed')",name="ck_alert_outbox_state"),
  schema="finance")
def downgrade():
 op.drop_table("alert_outbox",schema="finance")

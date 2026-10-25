"""Track delivery attempts conservatively. Revision ID: 0025_alert_delivery."""
from alembic import op
import sqlalchemy as sa
revision="0025_alert_delivery"
down_revision="0024_alert_outbox"
branch_labels=None
depends_on=None
def upgrade():
 op.add_column("alert_outbox",sa.Column("attempts",sa.Integer(),nullable=False,server_default="0"),schema="finance")
 op.add_column("alert_outbox",sa.Column("last_error",sa.String(250)),schema="finance")
 op.add_column("alert_outbox",sa.Column("started_at",sa.DateTime(timezone=True)),schema="finance")
 op.execute("ALTER TABLE finance.alert_outbox DROP CONSTRAINT ck_alert_outbox_state")
 op.create_check_constraint("ck_alert_outbox_state","alert_outbox","state IN ('pending','sending','sent','failed','uncertain')",schema="finance")
def downgrade():
 op.execute("ALTER TABLE finance.alert_outbox DROP CONSTRAINT ck_alert_outbox_state")
 op.create_check_constraint("ck_alert_outbox_state","alert_outbox","state IN ('pending','sent','failed')",schema="finance")
 for column in ["started_at","last_error","attempts"]:
  op.drop_column("alert_outbox",column,schema="finance")

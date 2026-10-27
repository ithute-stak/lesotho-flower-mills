"""Allow audit-preserving cancellation of draft recurring order plans only."""
from alembic import op
import sqlalchemy as sa
revision="0044_repeat_order_cancellations"
down_revision="0043_referral_plans"
branch_labels=None
depends_on=None

def upgrade():
 op.add_column("repeat_order_templates",sa.Column("cancelled_by",sa.String(255),nullable=True),schema="marketing")
 op.add_column("repeat_order_templates",sa.Column("cancelled_at",sa.DateTime(timezone=True),nullable=True),schema="marketing")
 op.add_column("repeat_order_templates",sa.Column("cancellation_reason",sa.String(500),nullable=True),schema="marketing")
 op.drop_constraint("ck_repeat_draft_only","repeat_order_templates",schema="marketing",type_="check")
 op.create_check_constraint("ck_repeat_draft_or_cancelled","repeat_order_templates","status IN ('draft','cancelled')",schema="marketing")
 op.create_check_constraint("ck_repeat_cancellation_details","repeat_order_templates","(status='draft' AND cancelled_at IS NULL AND cancelled_by IS NULL AND cancellation_reason IS NULL) OR (status='cancelled' AND cancelled_at IS NOT NULL AND cancelled_by IS NOT NULL AND cancellation_reason IS NOT NULL)",schema="marketing")

def downgrade():
 connection=op.get_bind()
 if connection.execute(sa.text("SELECT COUNT(*) FROM marketing.repeat_order_templates WHERE status='cancelled'")).scalar_one():
  raise RuntimeError("Refusing downgrade: cancelled repeat-order audit records exist")
 op.drop_constraint("ck_repeat_cancellation_details","repeat_order_templates",schema="marketing",type_="check")
 op.drop_constraint("ck_repeat_draft_or_cancelled","repeat_order_templates",schema="marketing",type_="check")
 op.create_check_constraint("ck_repeat_draft_only","repeat_order_templates","status='draft'",schema="marketing")
 op.drop_column("repeat_order_templates","cancellation_reason",schema="marketing")
 op.drop_column("repeat_order_templates","cancelled_at",schema="marketing")
 op.drop_column("repeat_order_templates","cancelled_by",schema="marketing")

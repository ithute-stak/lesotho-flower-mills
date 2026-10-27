"""Planning-only reviews of repeat-order templates; no execution privileges."""
from alembic import op
import sqlalchemy as sa
revision="0045_repeat_order_planning_reviews"
down_revision="0044_repeat_order_cancellations"
branch_labels=None
depends_on=None

def upgrade():
 op.drop_constraint("ck_repeat_draft_or_cancelled","repeat_order_templates",schema="marketing",type_="check")
 op.drop_constraint("ck_repeat_cancellation_details","repeat_order_templates",schema="marketing",type_="check")
 op.add_column("repeat_order_templates",sa.Column("reviewed_by",sa.String(255)),schema="marketing")
 op.add_column("repeat_order_templates",sa.Column("reviewed_at",sa.DateTime(timezone=True)),schema="marketing")
 op.add_column("repeat_order_templates",sa.Column("review_note",sa.String(500)),schema="marketing")
 op.create_check_constraint("ck_repeat_planning_status","repeat_order_templates","status IN ('draft','approved','rejected','cancelled')",schema="marketing")
 op.create_check_constraint("ck_repeat_planning_audit","repeat_order_templates","((status='draft' AND reviewed_by IS NULL AND reviewed_at IS NULL AND review_note IS NULL AND cancelled_by IS NULL AND cancelled_at IS NULL AND cancellation_reason IS NULL) OR (status IN ('approved','rejected') AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL AND review_note IS NOT NULL AND cancelled_by IS NULL AND cancelled_at IS NULL AND cancellation_reason IS NULL) OR (status='cancelled' AND cancelled_by IS NOT NULL AND cancelled_at IS NOT NULL AND cancellation_reason IS NOT NULL))",schema="marketing")
 op.create_table("repeat_order_review_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("template_id",sa.Uuid(),sa.ForeignKey("marketing.repeat_order_templates.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("action",sa.String(16),nullable=False),
  sa.Column("actor",sa.String(255),nullable=False),
  sa.Column("note",sa.String(500),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.CheckConstraint("action IN ('approved','rejected')",name="ck_repeat_review_action"),
  schema="marketing")

def downgrade():
 bind=op.get_bind()
 if bind.execute(sa.text("SELECT COUNT(*) FROM marketing.repeat_order_review_events")).scalar_one() or bind.execute(sa.text("SELECT COUNT(*) FROM marketing.repeat_order_templates WHERE status IN ('approved','rejected')")).scalar_one():
  raise RuntimeError("Cannot downgrade while repeat-order review audit records exist")
 op.drop_table("repeat_order_review_events",schema="marketing")
 op.drop_constraint("ck_repeat_planning_audit","repeat_order_templates",schema="marketing",type_="check")
 op.drop_constraint("ck_repeat_planning_status","repeat_order_templates",schema="marketing",type_="check")
 op.drop_column("repeat_order_templates","review_note",schema="marketing")
 op.drop_column("repeat_order_templates","reviewed_at",schema="marketing")
 op.drop_column("repeat_order_templates","reviewed_by",schema="marketing")
 op.create_check_constraint("ck_repeat_draft_or_cancelled","repeat_order_templates","status IN ('draft','cancelled')",schema="marketing")
 op.create_check_constraint("ck_repeat_cancellation_details","repeat_order_templates","(status='draft' AND cancelled_at IS NULL AND cancelled_by IS NULL AND cancellation_reason IS NULL) OR (status='cancelled' AND cancelled_at IS NOT NULL AND cancelled_by IS NOT NULL AND cancellation_reason IS NOT NULL)",schema="marketing")

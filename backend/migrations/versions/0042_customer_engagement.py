"""Customer engagement enrolment and repeat-order templates; no rewards or automatic ordering."""
from alembic import op
import sqlalchemy as sa
revision="0042_customer_engagement"
down_revision="0041_wholesale_tier_events"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("loyalty_enrolments",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("customer_id",sa.Uuid(),sa.ForeignKey("crm.customers.id",ondelete="RESTRICT"),nullable=False,unique=True),
  sa.Column("status",sa.String(16),nullable=False,server_default="draft"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("status='draft'",name="ck_loyalty_draft_only"),schema="marketing")
 op.create_table("repeat_order_templates",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("customer_id",sa.Uuid(),sa.ForeignKey("crm.customers.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("product_id",sa.Uuid(),sa.ForeignKey("catalog.products.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("quantity",sa.Integer(),nullable=False),
  sa.Column("frequency",sa.String(12),nullable=False),
  sa.Column("status",sa.String(16),nullable=False,server_default="draft"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("quantity BETWEEN 1 AND 1000000",name="ck_repeat_qty"),
  sa.CheckConstraint("frequency IN ('weekly','monthly')",name="ck_repeat_frequency"),
  sa.CheckConstraint("status='draft'",name="ck_repeat_draft_only"),schema="marketing")
def downgrade():
 op.drop_table("repeat_order_templates",schema="marketing")
 op.drop_table("loyalty_enrolments",schema="marketing")

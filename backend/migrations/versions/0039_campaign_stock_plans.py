"""Non-reserving promotion stock allocation planning."""
from alembic import op
import sqlalchemy as sa
revision="0039_campaign_stock_plans"
down_revision="0038_campaign_budgets"
branch_labels=None
depends_on=None

def upgrade():
 op.create_table("campaign_stock_plans",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("campaign_id",sa.Uuid(),sa.ForeignKey("marketing.campaigns.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("warehouse_id",sa.Uuid(),sa.ForeignKey("inventory.warehouses.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("product_id",sa.Uuid(),sa.ForeignKey("catalog.products.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("planned_quantity",sa.Integer(),nullable=False),
  sa.Column("status",sa.String(16),nullable=False,server_default="draft"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.UniqueConstraint("campaign_id","warehouse_id","product_id",name="uq_campaign_stock_plan"),
  sa.CheckConstraint("planned_quantity > 0",name="ck_campaign_stock_positive"),
  sa.CheckConstraint("status='draft'",name="ck_campaign_stock_draft_only"),
  schema="marketing")
def downgrade():
 op.drop_table("campaign_stock_plans",schema="marketing")

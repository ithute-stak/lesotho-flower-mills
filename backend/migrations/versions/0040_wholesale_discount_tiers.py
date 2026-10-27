"""Wholesale promotional tiers are planning records, not checkout pricing."""
from alembic import op
import sqlalchemy as sa
revision="0040_wholesale_discount_tiers"
down_revision="0039_campaign_stock_plans"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("wholesale_discount_tiers",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("campaign_id",sa.Uuid(),sa.ForeignKey("marketing.campaigns.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("product_id",sa.Uuid(),sa.ForeignKey("catalog.products.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("minimum_quantity",sa.Integer(),nullable=False),
  sa.Column("discount_bps",sa.Integer(),nullable=False),
  sa.Column("status",sa.String(16),nullable=False,server_default="draft"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("approved_by",sa.String(255)),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.UniqueConstraint("campaign_id","product_id","minimum_quantity",name="uq_wholesale_discount_break"),
  sa.CheckConstraint("minimum_quantity >= 2",name="ck_wholesale_min_qty"),
  sa.CheckConstraint("discount_bps BETWEEN 1 AND 10000",name="ck_wholesale_discount_bps"),
  sa.CheckConstraint("status IN ('draft','approved','disabled')",name="ck_wholesale_status"),
  schema="marketing")
def downgrade():
 op.drop_table("wholesale_discount_tiers",schema="marketing")

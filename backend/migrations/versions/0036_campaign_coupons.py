"""Campaign coupon inventory, with no checkout redemption pathway."""
from alembic import op
import sqlalchemy as sa
revision="0036_campaign_coupons"
down_revision="0035_commercial_campaigns"
branch_labels=None
depends_on=None

def upgrade():
 op.create_table("coupons",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("campaign_id",sa.Uuid(),sa.ForeignKey("marketing.campaigns.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("code",sa.String(64),nullable=False,unique=True),
  sa.Column("max_redemptions",sa.Integer(),nullable=False),
  sa.Column("redemption_count",sa.Integer(),nullable=False,server_default="0"),
  sa.Column("status",sa.String(16),nullable=False,server_default="draft"),
  sa.Column("created_by",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("max_redemptions > 0",name="ck_coupon_positive_limit"),
  sa.CheckConstraint("redemption_count >= 0 AND redemption_count <= max_redemptions",name="ck_coupon_redemptions"),
  sa.CheckConstraint("status IN ('draft','disabled')",name="ck_coupon_status"),
  schema="marketing")
 op.create_index("ix_coupons_campaign", "coupons", ["campaign_id"],schema="marketing")

def downgrade():
 op.drop_index("ix_coupons_campaign",table_name="coupons",schema="marketing")
 op.drop_table("coupons",schema="marketing")

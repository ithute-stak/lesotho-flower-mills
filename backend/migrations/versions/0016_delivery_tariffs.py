"""Delivery zone and tariff pricing configuration.

Revision ID: 0016_delivery_tariffs
Revises: 0015_order_totals
"""
from alembic import op
import sqlalchemy as sa
revision="0016_delivery_tariffs"
down_revision="0015_order_totals"
branch_labels=None
depends_on=None
def upgrade():
 op.execute("CREATE SCHEMA IF NOT EXISTS delivery")
 op.create_table("zones",
   sa.Column("id",sa.Uuid(),primary_key=True),
   sa.Column("code",sa.String(40),nullable=False,unique=True),
   sa.Column("name",sa.String(120),nullable=False),
   sa.Column("active",sa.Boolean(),nullable=False,server_default=sa.false()),
   schema="delivery")
 op.create_table("tariffs",
   sa.Column("id",sa.Uuid(),primary_key=True),
   sa.Column("zone_id",sa.Uuid(),sa.ForeignKey("delivery.zones.id",ondelete="RESTRICT"),nullable=False),
   sa.Column("version",sa.Integer(),nullable=False),
   sa.Column("flat_fee",sa.Numeric(18,2),nullable=False),
   sa.Column("free_delivery_minimum",sa.Numeric(18,2)),
   sa.Column("effective_from",sa.DateTime(timezone=True),nullable=False),
   sa.Column("effective_until",sa.DateTime(timezone=True)),
   sa.Column("approved",sa.Boolean(),nullable=False,server_default=sa.false()),
   sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
   sa.CheckConstraint("flat_fee>=0 AND (free_delivery_minimum IS NULL OR free_delivery_minimum>=0)",name="ck_tariff_nonnegative"),
   sa.CheckConstraint("effective_until IS NULL OR effective_until>effective_from",name="ck_tariff_dates"),
   sa.UniqueConstraint("zone_id","version",name="uq_zone_tariff_version"),
   schema="delivery")
def downgrade():
 op.drop_table("tariffs",schema="delivery")
 op.drop_table("zones",schema="delivery")

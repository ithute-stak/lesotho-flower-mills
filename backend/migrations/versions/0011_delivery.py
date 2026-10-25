"""Delivery assignments and tracking events.

Revision ID: 0011_delivery
Revises: 0010_payments
"""
from alembic import op
import sqlalchemy as sa
revision="0011_delivery"
down_revision="0010_payments"
branch_labels=None
depends_on=None
def upgrade():
 op.execute("CREATE SCHEMA IF NOT EXISTS delivery")
 op.create_table("drivers",sa.Column("id",sa.Uuid(),primary_key=True),sa.Column("identity_subject",sa.String(255),nullable=False,unique=True),sa.Column("display_name",sa.String(150),nullable=False),sa.Column("active",sa.Boolean(),nullable=False,server_default=sa.true()),schema="delivery")
 op.create_table("vehicles",sa.Column("id",sa.Uuid(),primary_key=True),sa.Column("registration",sa.String(40),nullable=False,unique=True),sa.Column("active",sa.Boolean(),nullable=False,server_default=sa.true()),schema="delivery")
 op.create_table("assignments",sa.Column("id",sa.Uuid(),primary_key=True),sa.Column("sales_order_id",sa.Uuid(),sa.ForeignKey("sales.sales_orders.id",ondelete="RESTRICT"),nullable=False,unique=True),sa.Column("driver_id",sa.Uuid(),sa.ForeignKey("delivery.drivers.id",ondelete="RESTRICT"),nullable=False),sa.Column("vehicle_id",sa.Uuid(),sa.ForeignKey("delivery.vehicles.id",ondelete="RESTRICT"),nullable=False),sa.Column("status",sa.String(24),nullable=False,server_default="assigned"),sa.Column("created_by",sa.String(255),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.CheckConstraint("status IN ('assigned','ready','dispatched','arrived','delivered','cancelled')",name="ck_delivery_status"),schema="delivery")
 op.create_table("events",sa.Column("id",sa.Uuid(),primary_key=True),sa.Column("assignment_id",sa.Uuid(),sa.ForeignKey("delivery.assignments.id",ondelete="RESTRICT"),nullable=False),sa.Column("event_type",sa.String(32),nullable=False),sa.Column("actor_id",sa.String(255),nullable=False),sa.Column("latitude",sa.Numeric(9,6)),sa.Column("longitude",sa.Numeric(9,6)),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),schema="delivery")
 op.create_index("ix_delivery_events_assignment","events",["assignment_id","created_at"],schema="delivery")
def downgrade():
 op.drop_index("ix_delivery_events_assignment",table_name="events",schema="delivery")
 for table in ("events","assignments","vehicles","drivers"):op.drop_table(table,schema="delivery")
 op.execute("DROP SCHEMA IF EXISTS delivery")

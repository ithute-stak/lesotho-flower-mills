"""Acknowledgement and discrepancies: evidence intake, not completed delivery.

Revision ID: 0013_delivery_disputes
Revises: 0012_pod
"""
from alembic import op
import sqlalchemy as sa
revision="0013_delivery_disputes"
down_revision="0012_pod"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("acknowledgements",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("assignment_id",sa.Uuid(),sa.ForeignKey("delivery.assignments.id",ondelete="RESTRICT"),nullable=False,unique=True),
  sa.Column("customer_subject",sa.String(255),nullable=False),
  sa.Column("decision",sa.String(20),nullable=False),
  sa.Column("remarks",sa.String(1000)),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.CheckConstraint("decision IN ('accepted','partial','rejected')",name="ck_ack_decision"),
  schema="delivery")
 op.create_table("discrepancies",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("acknowledgement_id",sa.Uuid(),sa.ForeignKey("delivery.acknowledgements.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("quotation_item_id",sa.Uuid(),sa.ForeignKey("sales.quotation_items.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("expected_quantity",sa.Integer(),nullable=False),
  sa.Column("received_quantity",sa.Integer(),nullable=False),
  sa.Column("reason",sa.String(400),nullable=False),
  sa.CheckConstraint("expected_quantity>0 AND received_quantity>=0 AND received_quantity<=expected_quantity",name="ck_delivery_discrepancy_quantity"),
  sa.UniqueConstraint("acknowledgement_id","quotation_item_id",name="uq_ack_item"),
  schema="delivery")
 op.create_table("disputes",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("acknowledgement_id",sa.Uuid(),sa.ForeignKey("delivery.acknowledgements.id",ondelete="RESTRICT"),nullable=False,unique=True),
  sa.Column("status",sa.String(24),nullable=False,server_default="open"),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.CheckConstraint("status IN ('open','under_review','resolved','closed')",name="ck_dispute_status"),
  schema="delivery")
def downgrade():
 for table in ("disputes","discrepancies","acknowledgements"):op.drop_table(table,schema="delivery")

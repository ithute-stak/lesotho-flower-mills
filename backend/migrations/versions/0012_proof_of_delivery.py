"""One-time delivery handover challenge and audit.

Revision ID: 0012_pod
Revises: 0011_delivery
"""
from alembic import op
import sqlalchemy as sa
revision="0012_pod"
down_revision="0011_delivery"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("handover_challenges",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("assignment_id",sa.Uuid(),sa.ForeignKey("delivery.assignments.id",ondelete="RESTRICT"),nullable=False,unique=True),
  sa.Column("code_hash",sa.String(128),nullable=False),
  sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),
  sa.Column("attempts",sa.Integer(),nullable=False,server_default="0"),
  sa.Column("consumed_at",sa.DateTime(timezone=True)),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.CheckConstraint("attempts >= 0",name="ck_pod_attempts"),schema="delivery")
 op.create_table("handover_events",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("assignment_id",sa.Uuid(),sa.ForeignKey("delivery.assignments.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("actor_subject",sa.String(255),nullable=False),
  sa.Column("event_type",sa.String(36),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  schema="delivery")
def downgrade():
 op.drop_table("handover_events",schema="delivery")
 op.drop_table("handover_challenges",schema="delivery")

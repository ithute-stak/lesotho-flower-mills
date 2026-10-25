"""Audited maker/checker grant requests. Revision ID: 0028_finance_grant_requests."""
from alembic import op
import sqlalchemy as sa
revision="0028_finance_grant_requests"
down_revision="0027_finance_roles"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("finance_grant_requests",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("identity_subject",sa.String(255),nullable=False),
  sa.Column("role",sa.String(32),nullable=False),
  sa.Column("requested_by",sa.String(255),nullable=False),
  sa.Column("reviewed_by",sa.String(255)),
  sa.Column("status",sa.String(20),nullable=False,server_default="pending"),
  sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  sa.Column("reviewed_at",sa.DateTime(timezone=True)),
  sa.CheckConstraint("role IN ('finance_viewer','finance_reviewer','finance_admin')",name="ck_grant_request_role"),
  sa.CheckConstraint("status IN ('pending','approved','rejected')",name="ck_grant_request_status"),
  sa.CheckConstraint("requested_by <> identity_subject",name="ck_grant_request_no_self"),
  sa.CheckConstraint("reviewed_by IS NULL OR reviewed_by <> requested_by",name="ck_grant_request_independent"),
  schema="finance")
 op.create_index("ix_finance_grant_requests_status","finance_grant_requests",["status","created_at"],schema="finance")
def downgrade():
 op.drop_index("ix_finance_grant_requests_status",table_name="finance_grant_requests",schema="finance")
 op.drop_table("finance_grant_requests",schema="finance")

"""DB-backed scoped finance grants. Revision ID: 0027_finance_roles."""
from alembic import op
import sqlalchemy as sa
revision="0027_finance_roles"
down_revision="0026_delivery_incidents"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("finance_role_grants",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("identity_subject",sa.String(255),nullable=False),
  sa.Column("role",sa.String(32),nullable=False),
  sa.Column("active",sa.Boolean(),nullable=False,server_default=sa.true()),
  sa.Column("granted_by",sa.String(255),nullable=False),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
  sa.Column("revoked_at",sa.DateTime(timezone=True)),
  sa.CheckConstraint("role IN ('finance_viewer','finance_reviewer','finance_admin')",name="ck_finance_role"),
  sa.UniqueConstraint("identity_subject","role",name="uq_finance_subject_role"),
  schema="finance")
 op.create_index("ix_finance_active_roles","finance_role_grants",["identity_subject","active"],schema="finance")
def downgrade():
 op.drop_index("ix_finance_active_roles",table_name="finance_role_grants",schema="finance")
 op.drop_table("finance_role_grants",schema="finance")

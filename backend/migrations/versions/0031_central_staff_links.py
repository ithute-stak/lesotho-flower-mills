"""Explicit centrally verified staff subject bindings."""
from alembic import op
import sqlalchemy as sa
revision="0031_central_staff_links"
down_revision="0030_oauth_replay"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("central_staff_links",
  sa.Column("id",sa.Uuid(),primary_key=True),
  sa.Column("issuer",sa.String(255),nullable=False),
  sa.Column("central_subject",sa.String(255),nullable=False),
  sa.Column("local_user_id",sa.Uuid(),sa.ForeignKey("identity.users.id",ondelete="RESTRICT"),nullable=False),
  sa.Column("active",sa.Boolean(),nullable=False,server_default=sa.false()),
  sa.Column("verified_by",sa.String(255)),
  sa.Column("verified_at",sa.DateTime(timezone=True)),
  sa.Column("revoked_at",sa.DateTime(timezone=True)),
  sa.UniqueConstraint("issuer","central_subject",name="uq_central_staff_subject"),
  sa.UniqueConstraint("local_user_id",name="uq_central_staff_local_user"),
  sa.CheckConstraint("NOT active OR (verified_by IS NOT NULL AND verified_at IS NOT NULL AND revoked_at IS NULL)",name="ck_central_staff_verified"),
  schema="identity")
def downgrade():
 op.drop_table("central_staff_links",schema="identity")

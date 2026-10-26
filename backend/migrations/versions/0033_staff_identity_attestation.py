"""Require externally attested ownership before staff link activation."""
from alembic import op
import sqlalchemy as sa
revision="0033_staff_identity_attestation"
down_revision="0032_staff_link_review"
branch_labels=None
depends_on=None
def upgrade():
 op.add_column("central_staff_links",sa.Column("attested_subject",sa.String(255)),schema="identity")
 op.add_column("central_staff_links",sa.Column("attested_issuer",sa.String(255)),schema="identity")
 op.add_column("central_staff_links",sa.Column("attested_at",sa.DateTime(timezone=True)),schema="identity")
 op.add_column("central_staff_links",sa.Column("attestation_reference",sa.String(255)),schema="identity")
 op.create_check_constraint("ck_staff_link_identity_attested","central_staff_links",
  "NOT active OR (attested_at IS NOT NULL AND attested_subject=central_subject AND attested_issuer=issuer AND attestation_reference IS NOT NULL)",schema="identity")
 # Any existing active links were approved without authenticated ownership evidence.
 op.execute("UPDATE identity.central_staff_links SET active=false, revoked_at=now() WHERE active=true")
def downgrade():
 op.drop_constraint("ck_staff_link_identity_attested","central_staff_links",schema="identity")
 for name in ("attestation_reference","attested_at","attested_issuer","attested_subject"):
  op.drop_column("central_staff_links",name,schema="identity")

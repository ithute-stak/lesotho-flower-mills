"""One-use OAuth state claims. Revision ID 0030_oauth_replay."""
from alembic import op
import sqlalchemy as sa
revision="0030_oauth_replay"
down_revision="0029_finance_grant_audit"
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("oauth_state_claims",
  sa.Column("state_digest",sa.String(64),primary_key=True),
  sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),
  sa.Column("claimed_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
  schema="public")
 op.create_index("ix_oauth_state_claims_expiry","oauth_state_claims",["expires_at"])
def downgrade():
 op.drop_index("ix_oauth_state_claims_expiry",table_name="oauth_state_claims")
 op.drop_table("oauth_state_claims")

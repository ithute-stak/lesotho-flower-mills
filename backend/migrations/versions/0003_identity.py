"""Identity users, separate from customer organisations.

Revision ID: 0003_identity
Revises: 0002_commerce
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_identity"
down_revision = "0002_commerce"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS identity")
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(254), unique=True, nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(40), nullable=False, server_default="customer"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('customer','admin','sales_manager')", name="ck_identity_role"),
        schema="identity",
    )
    op.create_index("ix_identity_users_email_lower", "users", [sa.text("lower(email)")], schema="identity", unique=True)


def downgrade():
    op.drop_index("ix_identity_users_email_lower", table_name="users", schema="identity")
    op.drop_table("users", schema="identity")
    op.execute("DROP SCHEMA IF EXISTS identity")

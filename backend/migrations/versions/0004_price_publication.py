"""Price book lifecycle and audit trail.

Revision ID: 0004_price_publication
Revises: 0003_identity
"""
from alembic import op
import sqlalchemy as sa
revision = "0004_price_publication"
down_revision = "0003_identity"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("price_books", sa.Column("status", sa.String(20), nullable=False, server_default="draft"), schema="pricing")
    op.add_column("price_books", sa.Column("reviewed_by", sa.String(255)), schema="pricing")
    op.add_column("price_books", sa.Column("reviewed_at", sa.DateTime(timezone=True)), schema="pricing")
    op.add_column("price_books", sa.Column("published_by", sa.String(255)), schema="pricing")
    op.add_column("price_books", sa.Column("published_at", sa.DateTime(timezone=True)), schema="pricing")
    op.create_check_constraint("ck_book_status", "price_books", "status IN ('draft','approved','published','retired')", schema="pricing")
    op.create_table("price_book_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("price_book_id", sa.Uuid(), sa.ForeignKey("pricing.price_books.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("actor_id", sa.String(255), nullable=False),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="pricing"
    )


def downgrade():
    op.drop_table("price_book_events", schema="pricing")
    op.drop_constraint("ck_book_status", "price_books", schema="pricing")
    for c in ["published_at","published_by","reviewed_at","reviewed_by","status"]:
        op.drop_column("price_books", c, schema="pricing")

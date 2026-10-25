"""Customer account relationships, business verification and price book structure.

Revision ID: 0002_commerce
Revises: 0001_foundation
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_commerce"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS pricing")
    op.create_table(
        "customer_users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("customer_id", sa.Uuid(), sa.ForeignKey("crm.customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("identity_subject", sa.String(255), nullable=False),
        sa.Column("membership_role", sa.String(30), nullable=False),
        sa.UniqueConstraint("customer_id", "identity_subject", name="uq_customer_member"),
        schema="crm",
    )
    op.create_table(
        "business_verifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("customer_id", sa.Uuid(), sa.ForeignKey("crm.customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("registration_number", sa.String(100)),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", sa.String(255)),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="ck_verification_status"),
        schema="crm",
    )
    op.create_table(
        "price_books",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="LSL"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.false()),
        schema="pricing",
    )
    op.create_table(
        "price_book_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("price_book_id", sa.Uuid(), sa.ForeignKey("pricing.price_books.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("catalog.products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("method", sa.String(24), nullable=False),
        sa.CheckConstraint("method IN ('fixed_bundle', 'volume_all_units')", name="ck_pricing_method"),
        sa.UniqueConstraint("price_book_id", "product_id", name="uq_pricebook_product"),
        schema="pricing",
    )
    op.create_table(
        "price_tiers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("price_book_item_id", sa.Uuid(), sa.ForeignKey("pricing.price_book_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("minimum_quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(18,4)),
        sa.Column("bundle_price", sa.Numeric(18,2)),
        sa.CheckConstraint("minimum_quantity >= 1", name="ck_positive_tier"),
        sa.CheckConstraint("(unit_price IS NULL) <> (bundle_price IS NULL)", name="ck_exactly_one_price"),
        sa.UniqueConstraint("price_book_item_id", "minimum_quantity", name="uq_tier_breakpoint"),
        schema="pricing",
    )


def downgrade() -> None:
    op.drop_table("price_tiers", schema="pricing")
    op.drop_table("price_book_items", schema="pricing")
    op.drop_table("price_books", schema="pricing")
    op.drop_table("business_verifications", schema="crm")
    op.drop_table("customer_users", schema="crm")
    op.execute("DROP SCHEMA IF EXISTS pricing")

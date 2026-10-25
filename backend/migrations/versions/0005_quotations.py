"""Create quotations with stored price snapshots.

Revision ID: 0005_quotations
Revises: 0004_price_publication
"""
from alembic import op
import sqlalchemy as sa
revision = "0005_quotations"
down_revision = "0004_price_publication"
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS sales")
    op.create_table(
        "quotations",
        sa.Column("id",sa.Uuid(),primary_key=True),
        sa.Column("quotation_number",sa.String(40),unique=True,nullable=False),
        sa.Column("customer_id",sa.Uuid(),sa.ForeignKey("crm.customers.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("price_book_id",sa.Uuid(),sa.ForeignKey("pricing.price_books.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("status",sa.String(20),nullable=False,server_default="draft"),
        sa.Column("currency",sa.String(3),nullable=False,server_default="LSL"),
        sa.Column("subtotal",sa.Numeric(18,2),nullable=False),
        sa.Column("created_by",sa.String(255),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("status IN ('draft','issued','expired','cancelled')",name="ck_quotation_status"),
        schema="sales",
    )
    op.create_table(
        "quotation_items",
        sa.Column("id",sa.Uuid(),primary_key=True),
        sa.Column("quotation_id",sa.Uuid(),sa.ForeignKey("sales.quotations.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("product_id",sa.Uuid(),sa.ForeignKey("catalog.products.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("sku_snapshot",sa.String(64),nullable=False),
        sa.Column("product_name_snapshot",sa.String(200),nullable=False),
        sa.Column("quantity",sa.Integer(),nullable=False),
        sa.Column("pricing_method_snapshot",sa.String(24),nullable=False),
        sa.Column("line_total",sa.Numeric(18,2),nullable=False),
        sa.CheckConstraint("quantity >= 1",name="ck_quotation_positive_quantity"),
        schema="sales",
    )
    op.create_index("ix_quotation_customer","quotations",["customer_id"],schema="sales")

def downgrade():
    op.drop_index("ix_quotation_customer",table_name="quotations",schema="sales")
    op.drop_table("quotation_items",schema="sales")
    op.drop_table("quotations",schema="sales")
    op.execute("DROP SCHEMA IF EXISTS sales")

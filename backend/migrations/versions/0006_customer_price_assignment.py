"""Customer-eligible pricing and quotation ownership.

Revision ID: 0006_customer_prices
Revises: 0005_quotations
"""
from alembic import op
import sqlalchemy as sa

revision="0006_customer_prices"
down_revision="0005_quotations"
branch_labels=None
depends_on=None

def upgrade():
    op.add_column("price_books",sa.Column("audience",sa.String(16),nullable=False,server_default="internal"),schema="pricing")
    op.create_check_constraint("ck_price_book_audience","price_books","audience IN ('internal','retail','business')",schema="pricing")
    op.create_table("customer_price_books",
        sa.Column("id",sa.Uuid(),primary_key=True),
        sa.Column("customer_id",sa.Uuid(),sa.ForeignKey("crm.customers.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("price_book_id",sa.Uuid(),sa.ForeignKey("pricing.price_books.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("created_by",sa.String(255),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
        sa.UniqueConstraint("customer_id","price_book_id",name="uq_customer_price_book"),
        schema="pricing")

def downgrade():
    op.drop_table("customer_price_books",schema="pricing")
    op.drop_constraint("ck_price_book_audience","price_books",schema="pricing")
    op.drop_column("price_books","audience",schema="pricing")

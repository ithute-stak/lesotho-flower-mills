"""Order total review and immutability controls.

Revision ID: 0017_total_approval
Revises: 0016_delivery_tariffs
"""
from alembic import op
import sqlalchemy as sa
revision="0017_total_approval"
down_revision="0016_delivery_tariffs"
branch_labels=None
depends_on=None
def upgrade():
 op.add_column("order_totals",sa.Column("review_status",sa.String(24),nullable=False,server_default="draft"),schema="finance")
 op.add_column("order_totals",sa.Column("created_by",sa.String(255)),schema="finance")
 op.add_column("order_totals",sa.Column("approved_at",sa.DateTime(timezone=True)),schema="finance")
 op.create_check_constraint("ck_total_review_status","order_totals","review_status IN ('draft','approved','rejected')",schema="finance")
 op.execute("""CREATE OR REPLACE FUNCTION finance.reject_approved_total_mutation()
 RETURNS trigger LANGUAGE plpgsql AS $$
 BEGIN
 IF OLD.review_status='approved' THEN
 RAISE EXCEPTION 'Approved order total cannot be modified or deleted';
 END IF;
 RETURN NEW;
 END $$""")
 op.execute("""CREATE TRIGGER trg_immutable_approved_total
 BEFORE UPDATE OR DELETE ON finance.order_totals
 FOR EACH ROW EXECUTE FUNCTION finance.reject_approved_total_mutation()""")
def downgrade():
 op.execute("DROP TRIGGER IF EXISTS trg_immutable_approved_total ON finance.order_totals")
 op.execute("DROP FUNCTION IF EXISTS finance.reject_approved_total_mutation()")
 op.drop_constraint("ck_total_review_status","order_totals",schema="finance")
 for col in ("approved_at","created_by","review_status"):op.drop_column("order_totals",col,schema="finance")

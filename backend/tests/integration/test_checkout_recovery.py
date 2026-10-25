"""Recovery journal schema enforces one initiating payment per order."""
import os
import pytest
from sqlalchemy import create_engine,text
pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

def test_durable_checkout_attempt_constraints():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 try:
  with engine.connect() as db:
   columns=db.execute(text("""SELECT column_name,is_nullable FROM information_schema.columns
   WHERE table_schema='finance' AND table_name='checkout_attempts'""")).all()
   names=dict(columns)
   assert names["sales_order_id"]=="NO"
   assert names["idempotency_key"]=="NO"
   assert names["amount"]=="NO"
   constraints=db.execute(text("""SELECT conname FROM pg_constraint
   WHERE conrelid='finance.checkout_attempts'::regclass AND contype='u'""")).scalars().all()
   assert any("sales_order_id" in name for name in constraints)
   assert any("idempotency_key" in name for name in constraints)
 finally:
  engine.dispose()

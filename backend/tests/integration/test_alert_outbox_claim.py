"""Verify database state constraints and exactly one outbox row per alert."""
import os
import pytest
from sqlalchemy import create_engine,text
pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

def test_alert_outbox_unique_reference_and_state_constraints():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 try:
  with engine.connect() as con:
   keys=con.execute(text("""SELECT conname FROM pg_constraint
   WHERE conrelid='finance.alert_outbox'::regclass AND contype='u'""")).scalars().all()
   assert any("alert_id" in key for key in keys)
   checks=con.execute(text("""SELECT pg_get_constraintdef(oid) FROM pg_constraint
   WHERE conrelid='finance.alert_outbox'::regclass AND contype='c'""")).scalars().all()
   assert any("uncertain" in expr and "sending" in expr for expr in checks)
 finally:
  engine.dispose()

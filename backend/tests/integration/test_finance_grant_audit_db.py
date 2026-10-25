"""Validate immutable grant audit enforcement in PostgreSQL."""
import os
import pytest
from sqlalchemy import create_engine,text
pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

def test_grant_events_immutable_trigger_installed():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 try:
  with engine.connect() as conn:
   triggers=conn.execute(text("""SELECT tgname FROM pg_trigger
   WHERE tgrelid='finance.finance_grant_events'::regclass AND NOT tgisinternal""")).scalars().all()
   assert "trg_finance_grant_events_immutable" in triggers
 finally:
  engine.dispose()

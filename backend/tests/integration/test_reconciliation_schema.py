import os
import pytest
from sqlalchemy import create_engine,text
pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")
def test_append_only_reconciliation_audit_trigger_exists():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 try:
  with engine.connect() as con:
   rows=con.execute(text("""SELECT tgname FROM pg_trigger
   WHERE tgrelid='finance.reconciliation_events'::regclass AND NOT tgisinternal""")).scalars().all()
   assert "trg_recon_events_immutable" in rows
 finally:
  engine.dispose()

"""PostgreSQL alert persistence and idempotent deduplication."""
import os
from uuid import uuid4
import pytest
from sqlalchemy import create_engine,text
from app.finance_alerts import persist_alerts
pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")
def test_alert_persistence_deduplicated():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 period="CI-"+uuid4().hex
 try:
  with engine.connect() as db:
   try:
    events=[("reconciliation_run_failed","critical","CI worker failure")]
    persist_alerts(db,events,period)
    persist_alerts(db,events,period)
    count=db.execute(text("""SELECT COUNT(*) FROM finance.operational_alerts
     WHERE dedupe_key=:key"""),{"key":"reconciliation_run_failed:"+period}).scalar_one()
    assert count==1
   finally:
    db.execute(text("DELETE FROM finance.operational_alerts WHERE dedupe_key=:key"),{"key":"reconciliation_run_failed:"+period})
    db.commit()
 finally:
  engine.dispose()

"""PostgreSQL-backed SMTP uncertainty and concurrency tests; no network/email sent."""
import os
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.alert_delivery import deliver_one

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

@pytest.fixture
def setup_alert(monkeypatch):
 monkeypatch.setenv("LFM_FINANCE_EMAIL_DELIVERY_ENABLED","true")
 monkeypatch.setenv("LFM_FINANCE_ALERT_RECIPIENT","finance@example.invalid")
 monkeypatch.setenv("LFM_FINANCE_ALERT_SENDER","system@example.invalid")
 monkeypatch.setenv("LFM_FINANCE_SMTP_HOST","example.invalid")
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"],pool_size=3)
 alert_id,outbox_id=uuid4(),uuid4()
 try:
  with engine.begin() as con:
   con.execute(text("""INSERT INTO finance.operational_alerts(id,code,dedupe_key,severity,details)
    VALUES (:id,'smtp_ci',:key,'warning','Safe CI message')"""),
    {"id":alert_id,"key":"ci-"+str(alert_id)})
   con.execute(text("""INSERT INTO finance.alert_outbox(id,alert_id,state)
    VALUES (:id,:alert,'pending')"""),{"id":outbox_id,"alert":alert_id})
  yield engine,outbox_id
 finally:
  with engine.begin() as con:
   con.execute(text("DELETE FROM finance.alert_outbox WHERE id=:id"),{"id":outbox_id})
   con.execute(text("DELETE FROM finance.operational_alerts WHERE id=:id"),{"id":alert_id})
  engine.dispose()

def test_smtp_disconnect_keeps_uncertain_and_not_automatically_retried(setup_alert):
 engine,oid=setup_alert
 def connection_lost(_message):raise ConnectionError("SMTP disconnected after acceptance")
 with Session(engine) as db:
  result=deliver_one(db,send=connection_lost)
 assert result["result"]=="uncertain"
 with engine.connect() as con:
  state,attempts=con.execute(text("SELECT state,attempts FROM finance.alert_outbox WHERE id=:id"),
    {"id":oid}).one()
 assert (state,attempts)==("uncertain",1)
 with Session(engine) as db:
  assert deliver_one(db,send=lambda _:pytest.fail("Never resend uncertain mail"))["processed"]==0

def test_concurrent_delivery_only_claims_once(setup_alert):
 engine,oid=setup_alert
 entered=Event(); release=Event()
 def hold_send(_message):
  entered.set()
  assert release.wait(timeout=10)
 with ThreadPoolExecutor(max_workers=2) as workers:
  def first():
   with Session(engine) as db:return deliver_one(db,send=hold_send)
  def second():
   with Session(engine) as db:return deliver_one(db,send=lambda _:pytest.fail("Duplicate delivery"))
  f1=workers.submit(first)
  assert entered.wait(timeout=10)
  f2=workers.submit(second)
  result2=f2.result(timeout=10)
  release.set()
  result1=f1.result(timeout=10)
 assert result1["result"]=="sent"
 assert result2["processed"]==0
 with engine.connect() as con:
  state,attempts=con.execute(text("SELECT state,attempts FROM finance.alert_outbox WHERE id=:id"),
    {"id":oid}).one()
 assert (state,attempts)==("sent",1)

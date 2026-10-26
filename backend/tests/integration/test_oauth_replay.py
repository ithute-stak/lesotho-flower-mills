import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.oauth_replay import claim_oauth_state
pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

def test_single_use_across_sessions():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"],pool_size=3)
 state="oauth-test-"+uuid4().hex
 expires=datetime.now(timezone.utc)+timedelta(minutes=5)
 try:
  def consume():
   with Session(engine) as session:
    return claim_oauth_state(session,state,expires)
  with ThreadPoolExecutor(max_workers=2) as workers:
   results=list(workers.map(lambda _:consume(),range(2)))
  assert sorted(results)==[False,True]
  assert consume() is False
 finally:
  import hashlib
  with engine.begin() as con:
   con.execute(text("DELETE FROM oauth_state_claims WHERE state_digest=:digest"),
     {"digest":hashlib.sha256(state.encode()).hexdigest()})
  engine.dispose()

def test_expired_state_cannot_be_claimed():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 try:
  with Session(engine) as session:
   assert claim_oauth_state(session,"expired-"+uuid4().hex,datetime.now(timezone.utc)-timedelta(seconds=1)) is False
 finally:
  engine.dispose()

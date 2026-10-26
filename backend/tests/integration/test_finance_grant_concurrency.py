"""Separate PostgreSQL connections verify finance grant race serialization.

Committed synthetic records remain only in disposable CI databases because audit
events are append-only. Never execute against production.
"""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.finance_role_admin import approve_grant,revoke_grant

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="Disposable PostgreSQL required")

@pytest.fixture
def finance_race():
 url=os.environ["LFM_TEST_DATABASE_URL"]
 assert "lfm_test" in url, "Refusing committed concurrency fixtures outside test database"
 engine=create_engine(url,pool_size=4)
 maker="ci-maker-"+uuid4().hex
 checker="ci-checker-"+uuid4().hex
 recipient="ci-recipient-"+uuid4().hex
 request_id,grant_id=uuid4(),uuid4()
 with engine.begin() as db:
  db.execute(text("""INSERT INTO finance.finance_grant_requests
   (id,identity_subject,role,requested_by,status)
   VALUES (:id,:subject,'finance_viewer',:maker,'pending')"""),
   {"id":request_id,"subject":recipient,"maker":maker})
  db.execute(text("""INSERT INTO finance.finance_role_grants
   (id,identity_subject,role,granted_by,active)
   VALUES (:id,:subject,'finance_admin','ci',true)"""),
   {"id":grant_id,"subject":checker})
 yield engine,request_id,grant_id,checker,recipient
 engine.dispose()

def test_double_approval_serializes_and_audits_once(finance_race):
 engine,request_id,_,checker,recipient=finance_race
 barrier=Barrier(2)
 def run():
  with Session(engine) as db:
   barrier.wait(timeout=15)
   try:
    approve_grant(request_id,{"sub":checker,"role":"admin"},db)
    return 200
   except HTTPException as exc:
    db.rollback()
    return exc.status_code
 with ThreadPoolExecutor(max_workers=2) as pool:
  results=[pool.submit(run) for _ in range(2)]
  assert sorted(f.result(timeout=25) for f in results)==[200,409]
 with engine.connect() as db:
  assert db.execute(text("""SELECT COUNT(*) FROM finance.finance_role_grants
   WHERE identity_subject=:s AND role='finance_viewer' AND active=true"""),{"s":recipient}).scalar_one()==1
  assert db.execute(text("""SELECT COUNT(*) FROM finance.finance_grant_events
   WHERE request_id=:id AND action='approved'"""),{"id":request_id}).scalar_one()==1

def test_double_revocation_serializes_and_audits_once(finance_race):
 engine,_,_,checker,recipient=finance_race
 grant_id=uuid4()
 with engine.begin() as db:
  db.execute(text("""INSERT INTO finance.finance_role_grants
   (id,identity_subject,role,granted_by,active)
   VALUES (:id,:s,'finance_viewer',:checker,true)"""),
   {"id":grant_id,"s":recipient,"checker":checker})
 barrier=Barrier(2)
 def run():
  with Session(engine) as db:
   barrier.wait(timeout=15)
   try:
    revoke_grant(grant_id,{"sub":checker,"role":"admin"},db)
    return 200
   except HTTPException as exc:
    db.rollback()
    return exc.status_code
 with ThreadPoolExecutor(max_workers=2) as pool:
  results=[pool.submit(run) for _ in range(2)]
  assert sorted(f.result(timeout=25) for f in results)==[200,409]
 with engine.connect() as db:
  assert db.execute(text("SELECT active FROM finance.finance_role_grants WHERE id=:id"),{"id":grant_id}).scalar_one() is False
  assert db.execute(text("""SELECT COUNT(*) FROM finance.finance_grant_events
   WHERE grant_id=:id AND action='revoked'"""),{"id":grant_id}).scalar_one()==1

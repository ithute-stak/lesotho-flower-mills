"""PostgreSQL finance grant revocation and row-lock integrity checks."""
import os
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.finance_permissions import finance_read

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

def test_revocation_immediately_denies_existing_identity_token():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 id,subject=uuid4(),"ci-"+uuid4().hex
 identity={"sub":subject,"role":"admin"}
 try:
  with engine.begin() as con:
   con.execute(text("""INSERT INTO finance.finance_role_grants
   (id,identity_subject,role,active,granted_by)
   VALUES (:id,:subject,'finance_viewer',true,'ci-system')"""),{"id":id,"subject":subject})
  with Session(engine) as db:
   assert finance_read(identity,db)==identity
  with engine.begin() as con:
   con.execute(text("""UPDATE finance.finance_role_grants
   SET active=false,revoked_at=now() WHERE id=:id"""),{"id":id})
  with Session(engine) as db:
   with pytest.raises(HTTPException) as exc:
    finance_read(identity,db)
   assert exc.value.status_code==403
 finally:
  with engine.begin() as con:
   con.execute(text("DELETE FROM finance.finance_role_grants WHERE id=:id"),{"id":id})
  engine.dispose()

def test_concurrent_approval_row_lock_serializes_reviewers():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"],pool_size=3)
 request_id=uuid4()
 subject="ci-"+uuid4().hex
 locked=Event(); release=Event()
 try:
  with engine.begin() as con:
   con.execute(text("""INSERT INTO finance.finance_grant_requests
    (id,identity_subject,role,requested_by,status)
    VALUES (:id,:subject,'finance_viewer','ci-maker','pending')"""),
    {"id":request_id,"subject":subject})
  def first():
   with engine.begin() as con:
    row=con.execute(text("""SELECT status FROM finance.finance_grant_requests
      WHERE id=:id FOR UPDATE"""),{"id":request_id}).scalar_one()
    locked.set()
    assert release.wait(timeout=10)
    con.execute(text("""UPDATE finance.finance_grant_requests SET status='approved'
      WHERE id=:id"""),{"id":request_id})
    return row
  def second():
   with engine.begin() as con:
    con.execute(text("SET LOCAL lock_timeout='5s'"))
    return con.execute(text("""SELECT status FROM finance.finance_grant_requests
     WHERE id=:id FOR UPDATE"""),{"id":request_id}).scalar_one()
  with ThreadPoolExecutor(max_workers=2) as executor:
   first_result=executor.submit(first)
   assert locked.wait(timeout=10)
   second_result=executor.submit(second)
   release.set()
   assert first_result.result(timeout=10)=="pending"
   assert second_result.result(timeout=10)=="approved"
 finally:
  with engine.begin() as con:
   con.execute(text("DELETE FROM finance.finance_grant_requests WHERE id=:id"),{"id":request_id})
  engine.dispose()

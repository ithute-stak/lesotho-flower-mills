"""Complete finance permission lifecycle in rollback-only PostgreSQL test."""
import os
from uuid import UUID,uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.finance_role_admin import GrantRequest,request_grant,approve_grant,revoke_grant
from app.finance_permissions import finance_admin,finance_read

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

def test_request_approval_access_revocation_and_immediate_denial():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 conn=engine.connect()
 outer=conn.begin()
 db=Session(bind=conn,join_transaction_mode="create_savepoint")
 maker={"sub":"ci-maker-"+uuid4().hex,"role":"admin"}
 checker={"sub":"ci-checker-"+uuid4().hex,"role":"admin"}
 recipient={"sub":"ci-recipient-"+uuid4().hex,"role":"admin"}
 try:
  for actor in (maker,checker):
   db.execute(text("""INSERT INTO finance.finance_role_grants
    (id,identity_subject,role,granted_by,active)
    VALUES (:id,:subject,'finance_admin','independent-ci-setup',true)"""),
    {"id":uuid4(),"subject":actor["sub"]})
  db.flush()
  with pytest.raises(HTTPException) as denied:
   finance_read(recipient,db)
  assert denied.value.status_code==403
  request=request_grant(GrantRequest(identity_subject=recipient["sub"],role="finance_viewer"),maker,db)
  request_id=UUID(request["request_id"])
  with pytest.raises(HTTPException) as self_review:
   approve_grant(request_id,maker,db)
  assert self_review.value.status_code==403
  assert approve_grant(request_id,checker,db)["status"]=="approved"
  assert finance_read(recipient,db)==recipient
  with pytest.raises(HTTPException) as elevated:
   finance_admin(recipient,db)
  assert elevated.value.status_code==403
  grant_id=db.execute(text("""SELECT id FROM finance.finance_role_grants
   WHERE identity_subject=:s AND role='finance_viewer'"""),{"s":recipient["sub"]}).scalar_one()
  with pytest.raises(HTTPException) as self_revoke:
   revoke_grant(grant_id,recipient,db)
  assert self_revoke.value.status_code==403
  assert revoke_grant(grant_id,checker,db)["status"]=="revoked"
  with pytest.raises(HTTPException) as revoked:
   finance_read(recipient,db)
  assert revoked.value.status_code==403
  with pytest.raises(HTTPException) as duplicate:
   revoke_grant(grant_id,checker,db)
  assert duplicate.value.status_code==409
  events=db.execute(text("""SELECT action,actor FROM finance.finance_grant_events
   WHERE subject=:s"""),{"s":recipient["sub"]}).all()
  assert {action for action,_ in events}=={"requested","approved","revoked"}
  assert {actor for _,actor in events}=={maker["sub"],checker["sub"]}
 finally:
  db.close()
  outer.rollback()
  conn.close()
  engine.dispose()

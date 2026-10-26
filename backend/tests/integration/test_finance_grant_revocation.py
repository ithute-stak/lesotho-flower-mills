"""PostgreSQL finance-grant revocation takes effect for an unchanged token."""
import os
from uuid import uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.finance_permissions import finance_read,finance_admin

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

def test_revoked_finance_grant_denies_existing_identity_immediately():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 connection=engine.connect()
 outer=connection.begin()
 db=Session(bind=connection,join_transaction_mode="create_savepoint")
 identity={"sub":"ci-revoke-"+uuid4().hex,"role":"admin"}
 grant_id=uuid4()
 try:
  db.execute(text("""INSERT INTO finance.finance_role_grants
    (id,identity_subject,role,granted_by,active,revoked_at)
    VALUES (:id,:subject,'finance_admin','ci-independent',true,NULL)"""),
    {"id":grant_id,"subject":identity["sub"]})
  db.flush()
  assert finance_read(identity,db)==identity
  assert finance_admin(identity,db)==identity
  db.execute(text("""UPDATE finance.finance_role_grants
   SET active=false,revoked_at=now() WHERE id=:id"""),{"id":grant_id})
  db.flush()
  for permission in (finance_read,finance_admin):
   with pytest.raises(HTTPException) as error:
    permission(identity,db)
   assert error.value.status_code==403
 finally:
  db.close()
  outer.rollback()
  connection.close()
  engine.dispose()

def test_granted_administrator_cannot_request_own_finance_role():
 from app.finance_role_admin import GrantRequest,request_grant
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 connection=engine.connect()
 outer=connection.begin()
 db=Session(bind=connection,join_transaction_mode="create_savepoint")
 identity={"sub":"ci-selfgrant-"+uuid4().hex,"role":"admin"}
 try:
  with pytest.raises(HTTPException) as error:
   request_grant(GrantRequest(identity_subject=identity["sub"],role="finance_admin"),identity,db)
  assert error.value.status_code==403
  assert db.execute(text("SELECT COUNT(*) FROM finance.finance_grant_requests WHERE requested_by=:s"),{"s":identity["sub"]}).scalar_one()==0
 finally:
  db.close()
  outer.rollback()
  connection.close()
  engine.dispose()

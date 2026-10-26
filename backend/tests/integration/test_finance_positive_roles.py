"""Positive and negative finance role hierarchy tests against PostgreSQL."""
import os
from uuid import uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.finance_permissions import finance_read,finance_review,finance_admin

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")
ROLES={
 "finance_viewer":(True,False,False),
 "finance_reviewer":(True,True,False),
 "finance_admin":(True,True,True),
}

@pytest.mark.parametrize("role,expected",ROLES.items())
def test_active_grant_enforces_exact_role_hierarchy(role,expected):
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 conn=engine.connect()
 outer=conn.begin()
 db=Session(bind=conn,join_transaction_mode="create_savepoint")
 identity={"sub":"ci-permissions-"+uuid4().hex,"role":"admin"}
 try:
  db.execute(text("""INSERT INTO finance.finance_role_grants
   (id,identity_subject,role,granted_by,active,revoked_at)
   VALUES (:id,:subject,:role,'ci-independent',true,NULL)"""),
   {"id":uuid4(),"subject":identity["sub"],"role":role})
  db.flush()
  for dependency,allowed in zip((finance_read,finance_review,finance_admin),expected):
   if allowed:
    assert dependency(identity,db)==identity
   else:
    with pytest.raises(HTTPException) as denied:
     dependency(identity,db)
    assert denied.value.status_code==403
 finally:
  db.close()
  outer.rollback()
  conn.close()
  engine.dispose()

def test_non_admin_identity_cannot_elevate_using_finance_grant():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 conn=engine.connect()
 outer=conn.begin()
 db=Session(bind=conn,join_transaction_mode="create_savepoint")
 subject="ci-untrusted-"+uuid4().hex
 try:
  db.execute(text("""INSERT INTO finance.finance_role_grants
   (id,identity_subject,role,granted_by,active)
   VALUES (:id,:subject,'finance_admin','ci-independent',true)"""),
   {"id":uuid4(),"subject":subject})
  db.flush()
  for role in ("customer","sales_manager"):
   with pytest.raises(HTTPException) as denied:
    finance_admin({"sub":subject,"role":role},db)
   assert denied.value.status_code==403
 finally:
  db.close()
  outer.rollback()
  conn.close()
  engine.dispose()

"""Finance grant maker/checker guarantees against real disposable PostgreSQL."""
import os
from uuid import UUID,uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.finance_role_admin import GrantRequest,request_grant,approve_grant
from app.finance_permissions import finance_admin

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

@pytest.fixture
def financial_db():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 conn=engine.connect()
 outer=conn.begin()
 db=Session(bind=conn,join_transaction_mode="create_savepoint")
 try:
  yield db
 finally:
  db.close()
  outer.rollback()
  conn.close()
  engine.dispose()

def test_independent_reviewer_required_and_audited(financial_db):
 db=financial_db
 maker={"sub":"ci-maker-"+uuid4().hex,"role":"admin"}
 checker={"sub":"ci-checker-"+uuid4().hex,"role":"admin"}
 recipient={"sub":"ci-recipient-"+uuid4().hex,"role":"admin"}
 # API dependencies enforce each acting admin's active grant; fixtures create
 # no password, external identity or finance bootstrap mechanism.
 for actor in (maker,checker):
  db.execute(text("""INSERT INTO finance.finance_role_grants
    (id,identity_subject,role,granted_by,active)
    VALUES (:id,:subject,'finance_admin','ci-independent',true)"""),
    {"id":uuid4(),"subject":actor["sub"]})
 db.flush()
 assert finance_admin(maker,db)==maker
 assert finance_admin(checker,db)==checker
 requested=request_grant(GrantRequest(identity_subject=recipient["sub"],role="finance_viewer"),maker,db)
 request_id=UUID(requested["request_id"])
 for identity in (maker,recipient):
  with pytest.raises(HTTPException) as exc:
   approve_grant(request_id,identity,db)
  assert exc.value.status_code==403
 assert db.execute(text("""SELECT COUNT(*) FROM finance.finance_role_grants
 WHERE identity_subject=:subject AND role='finance_viewer'"""),{"subject":recipient["sub"]}).scalar_one()==0
 approved=approve_grant(request_id,checker,db)
 assert approved["status"]=="approved"
 assert db.execute(text("""SELECT active FROM finance.finance_role_grants
 WHERE identity_subject=:subject AND role='finance_viewer'"""),{"subject":recipient["sub"]}).scalar_one() is True
 assert db.execute(text("""SELECT action FROM finance.finance_grant_events
 WHERE request_id=:id ORDER BY created_at,action"""),{"id":request_id}).scalars().all()==["approved","requested"]
 with pytest.raises(HTTPException) as exc:
  approve_grant(request_id,checker,db)
 assert exc.value.status_code==409

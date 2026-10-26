"""Central identity security matrix at the PostgreSQL boundary.

The pipeline remains internal; test identities are artificial and cleaned up.
"""
import os
from uuid import uuid4
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.central_auth_pipeline import resolve_verified_central_staff
from app.finance_permissions import finance_read
pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

def test_active_link_and_finance_grant_revocation():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 local_id,link_id,grant_id=uuid4(),uuid4(),uuid4()
 central="ci-"+uuid4().hex
 issuer="https://auth.example.invalid"
 try:
  with engine.begin() as con:
   con.execute(text("""INSERT INTO identity.users(id,email,password_hash,role,active)
    VALUES(:id,:email,'test-not-a-password','admin',true)"""),
    {"id":local_id,"email":central+"@example.invalid"})
   con.execute(text("""INSERT INTO identity.central_staff_links
    (id,issuer,central_subject,local_user_id,active,verified_by,verified_at,
     attested_issuer,attested_subject,attested_at,attestation_reference)
    VALUES(:id,:issuer,:subject,:local,true,'ci-auditor',now(),
     :issuer,:subject,now(),'ci-attestation')"""),
    {"id":link_id,"issuer":issuer,"subject":central,"local":local_id})
   con.execute(text("""INSERT INTO finance.finance_role_grants
    (id,identity_subject,role,active,granted_by)
    VALUES(:id,:subject,'finance_viewer',true,'ci-auditor')"""),
    {"id":grant_id,"subject":str(local_id)})
  with Session(engine) as db:
   identity=resolve_verified_central_staff(db,verified_claims={"iss":issuer,"sub":central},session_active=True)
   assert identity["sub"]==str(local_id)
   assert finance_read(identity,db)==identity
  with engine.begin() as con:
   con.execute(text("UPDATE finance.finance_role_grants SET active=false,revoked_at=now() WHERE id=:id"),{"id":grant_id})
  with Session(engine) as db:
   identity=resolve_verified_central_staff(db,verified_claims={"iss":issuer,"sub":central},session_active=True)
   with pytest.raises(HTTPException) as exc:
    finance_read(identity,db)
   assert exc.value.status_code==403
  with engine.begin() as con:
   con.execute(text("UPDATE identity.central_staff_links SET active=false,revoked_at=now() WHERE id=:id"),{"id":link_id})
  with Session(engine) as db:
   with pytest.raises(HTTPException) as exc:
    resolve_verified_central_staff(db,verified_claims={"iss":issuer,"sub":central},session_active=True)
   assert exc.value.status_code==403
 finally:
  with engine.begin() as con:
   con.execute(text("DELETE FROM finance.finance_role_grants WHERE id=:id"),{"id":grant_id})
   con.execute(text("DELETE FROM identity.central_staff_links WHERE id=:id"),{"id":link_id})
   con.execute(text("DELETE FROM identity.users WHERE id=:id"),{"id":local_id})
  engine.dispose()

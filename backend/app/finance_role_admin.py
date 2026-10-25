"""Finance grant maker/checker actions. No automatic bootstrap or self-grant."""
from uuid import UUID,uuid4
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .finance_permissions import finance_admin
from .db import db_session

router=APIRouter(prefix="/api/v1/admin/finance-roles",tags=["finance-roles"])
class GrantRequest(BaseModel):
 identity_subject:str=Field(min_length=2,max_length=255)
 role:Literal["finance_viewer","finance_reviewer","finance_admin"]

@router.post("/requests",status_code=201)
def request_grant(body:GrantRequest,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 if body.identity_subject==identity["sub"]:
  raise HTTPException(403,"Cannot request your own finance permissions")
 request_id=uuid4()
 db.execute(text("""INSERT INTO finance.finance_grant_requests
 (id,identity_subject,role,requested_by)
 VALUES (:id,:target,:role,:actor)"""),
 {"id":request_id,"target":body.identity_subject,"role":body.role,"actor":identity["sub"]})
 db.execute(text("""INSERT INTO finance.finance_grant_events
 (id,request_id,subject,role,action,actor) VALUES (:id,:request,:subject,:role,'requested',:actor)"""),
 {"id":uuid4(),"request":request_id,"subject":body.identity_subject,"role":body.role,"actor":identity["sub"]})
 db.commit()
 return {"request_id":str(request_id),"status":"pending"}

@router.post("/requests/{request_id}/approve")
def approve_grant(request_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT identity_subject,role,requested_by,status
 FROM finance.finance_grant_requests WHERE id=:id FOR UPDATE"""),
 {"id":request_id}).mappings().first()
 if not row:raise HTTPException(404,"Grant request not found")
 if row["status"]!="pending":raise HTTPException(409,"Request already reviewed")
 if identity["sub"] in (row["requested_by"],row["identity_subject"]):
  raise HTTPException(403,"Independent reviewer required")
 db.execute(text("""INSERT INTO finance.finance_role_grants
 (id,identity_subject,role,granted_by,active,revoked_at)
 VALUES (:id,:subject,:role,:actor,true,NULL)
 ON CONFLICT(identity_subject,role)
 DO UPDATE SET active=true,revoked_at=NULL,granted_by=EXCLUDED.granted_by"""),
 {"id":uuid4(),"subject":row["identity_subject"],"role":row["role"],"actor":identity["sub"]})
 grant_id=db.execute(text("""SELECT id FROM finance.finance_role_grants
 WHERE identity_subject=:subject AND role=:role"""),
 {"subject":row["identity_subject"],"role":row["role"]}).scalar_one()
 db.execute(text("""INSERT INTO finance.finance_grant_events
 (id,request_id,grant_id,subject,role,action,actor)
 VALUES (:id,:request,:grant,:subject,:role,'approved',:actor)"""),
 {"id":uuid4(),"request":request_id,"grant":grant_id,"subject":row["identity_subject"],"role":row["role"],"actor":identity["sub"]})
 db.execute(text("""UPDATE finance.finance_grant_requests
 SET status='approved',reviewed_by=:actor,reviewed_at=now() WHERE id=:id"""),
 {"id":request_id,"actor":identity["sub"]})
 db.commit()
 return {"status":"approved","request_id":str(request_id)}

@router.post("/grants/{grant_id}/revoke")
def revoke_grant(grant_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT identity_subject,role,active FROM finance.finance_role_grants
 WHERE id=:id FOR UPDATE"""),{"id":grant_id}).mappings().first()
 if not row:raise HTTPException(404,"Grant not found")
 if row["identity_subject"]==identity["sub"]:
  raise HTTPException(403,"Cannot revoke your own finance grant")
 if not row["active"]:raise HTTPException(409,"Grant already inactive")
 db.execute(text("""UPDATE finance.finance_role_grants SET active=false,revoked_at=now()
 WHERE id=:id"""),{"id":grant_id})
 db.execute(text("""INSERT INTO finance.finance_grant_events
 (id,grant_id,subject,role,action,actor)
 VALUES (:id,:grant,:subject,:role,'revoked',:actor)"""),
 {"id":uuid4(),"grant":grant_id,"subject":row["identity_subject"],"role":row["role"],"actor":identity["sub"]})
 db.commit()
 return {"status":"revoked"}

@router.get("/grants")
def grants(identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 return [dict(r) for r in db.execute(text("""SELECT id,identity_subject,role,active,granted_by,
 created_at,revoked_at FROM finance.finance_role_grants
 ORDER BY created_at DESC LIMIT 200""")).mappings().all()]

@router.get("/events")
def audit_events(identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 return [dict(r) for r in db.execute(text("""SELECT subject,role,action,actor,created_at
 FROM finance.finance_grant_events ORDER BY created_at DESC LIMIT 200""")).mappings().all()]

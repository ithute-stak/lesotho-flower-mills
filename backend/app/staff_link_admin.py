"""Conservative two-person management of LFM staff identity links."""
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .finance_permissions import finance_admin
from .db import db_session

router=APIRouter(prefix="/api/v1/admin/central-staff-links",tags=["central-staff-links"])
class LinkRequest(BaseModel):
 issuer:str=Field(min_length=12,max_length=255)
 central_subject:str=Field(min_length=2,max_length=255)
 local_user_id:UUID

@router.post("/requests",status_code=201)
def request_link(body:LinkRequest,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 if not body.issuer.startswith("https://"):raise HTTPException(422,"HTTPS issuer required")
 local=db.execute(text("SELECT role,active FROM identity.users WHERE id=:id"),{"id":body.local_user_id}).mappings().first()
 if not local or not local["active"] or local["role"] not in ("admin","sales_manager"):
  raise HTTPException(422,"Active local staff account required")
 link_id=uuid4()
 db.execute(text("""INSERT INTO identity.central_staff_links
 (id,issuer,central_subject,local_user_id,requested_by)
 VALUES (:id,:issuer,:subject,:local,:actor)"""),
 {"id":link_id,"issuer":body.issuer,"subject":body.central_subject,"local":body.local_user_id,"actor":identity["sub"]})
 _event(db,link_id,"requested",identity["sub"])
 db.commit()
 return {"link_id":str(link_id),"active":False}

def _event(db,link_id,action,actor):
 db.execute(text("""INSERT INTO identity.central_staff_link_events(id,link_id,action,actor)
 VALUES (:id,:link,:action,:actor)"""),{"id":uuid4(),"link":link_id,"action":action,"actor":actor})

@router.post("/{link_id}/verify")
def verify_link(link_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT requested_by,active,revoked_at,local_user_id
 FROM identity.central_staff_links WHERE id=:id FOR UPDATE"""),{"id":link_id}).mappings().first()
 if not row:raise HTTPException(404,"Identity link not found")
 if row["active"] or row["revoked_at"]:raise HTTPException(409,"Link already reviewed or revoked")
 if identity["sub"] in (row["requested_by"],str(row["local_user_id"])):
  raise HTTPException(403,"Independent reviewer required")
 db.execute(text("""UPDATE identity.central_staff_links SET active=true,
 verified_by=:actor,verified_at=now() WHERE id=:id"""),{"id":link_id,"actor":identity["sub"]})
 _event(db,link_id,"verified",identity["sub"])
 db.commit()
 return {"active":True}

@router.post("/{link_id}/revoke")
def revoke_link(link_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT active FROM identity.central_staff_links
 WHERE id=:id FOR UPDATE"""),{"id":link_id}).mappings().first()
 if not row:raise HTTPException(404,"Identity link not found")
 if not row["active"]:raise HTTPException(409,"Link not active")
 db.execute(text("""UPDATE identity.central_staff_links SET active=false,revoked_at=now()
 WHERE id=:id"""),{"id":link_id})
 _event(db,link_id,"revoked",identity["sub"])
 db.commit()
 return {"active":False}

@router.get("/{link_id}/history")
def link_history(link_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 return [dict(r) for r in db.execute(text("""SELECT action,actor,created_at
 FROM identity.central_staff_link_events WHERE link_id=:id ORDER BY created_at"""),
 {"id":link_id}).mappings().all()]

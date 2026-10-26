"""Finance policy draft and independent approval. Not a tax-compliance certification."""
from datetime import datetime,timezone
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .finance_permissions import finance_read,finance_review,finance_admin
from .db import db_session

router=APIRouter(prefix="/api/v1/admin/financial-policies",tags=["financial-policies"])
class NewPolicy(BaseModel):
 code:str=Field(min_length=3,max_length=80,pattern=r"^[A-Za-z0-9_-]+$")
 version:int=Field(ge=1)
 tax_rate_bps:int=Field(ge=0,le=10000)
 delivery_taxable:bool=False
 max_discount_bps:int=Field(ge=0,le=10000)

@router.post("",status_code=201)
def create_policy(body:NewPolicy,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 pid=uuid4()
 try:
  db.execute(text("""INSERT INTO finance.financial_policies
   (id,code,version,tax_rate_bps,delivery_taxable,max_discount_bps,created_by)
   VALUES (:id,:code,:version,:tax,:freight,:discount,:actor)"""),
   {"id":pid,"code":body.code,"version":body.version,"tax":body.tax_rate_bps,
    "freight":body.delivery_taxable,"discount":body.max_discount_bps,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Policy version already exists")
 return {"id":str(pid),"status":"draft","effective":False}

@router.post("/{policy_id}/approve")
def approve_policy(policy_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT created_by,status FROM finance.financial_policies
 WHERE id=:id FOR UPDATE"""),{"id":policy_id}).mappings().first()
 if not row:raise HTTPException(404,"Policy not found")
 if row["status"]!="draft":raise HTTPException(409,"Only draft policies can be approved")
 if row["created_by"]==identity["sub"]:raise HTTPException(403,"Policy creator cannot approve their own policy")
 # Approval does not certify whether the proposed tax rate complies with Lesotho law.
 db.execute(text("""UPDATE finance.financial_policies SET status='approved',approved_by=:actor,
 effective_from=now() WHERE id=:id"""),{"id":policy_id,"actor":identity["sub"]})
 db.commit()
 return {"id":str(policy_id),"status":"approved","requires_tax_and_tariff_validation":True}

@router.get("")
def list_policies(identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,code,version,tax_rate_bps,delivery_taxable,max_discount_bps,
 status,created_by,approved_by,effective_from FROM finance.financial_policies
 ORDER BY code,version DESC LIMIT 200""")).mappings().all()
 return [dict(row) for row in rows]

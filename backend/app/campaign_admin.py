"""Finance-controlled campaign drafting and approval; never changes checkout totals."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field,model_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import db_session
from .finance_permissions import finance_read,finance_review,finance_admin

router=APIRouter(prefix="/api/v1/admin/campaigns",tags=["campaigns"])

class CampaignDraft(BaseModel):
 code:str=Field(min_length=3,max_length=80,pattern=r"^[A-Za-z0-9_-]+$")
 discount_bps:int=Field(ge=0,le=10000)
 minimum_subtotal:Decimal=Field(default=Decimal("0"),ge=0,max_digits=18,decimal_places=2)
 maximum_discount:Decimal|None=Field(default=None,ge=0,max_digits=18,decimal_places=2)
 audience:Literal["public","business"]
 starts_at:datetime
 ends_at:datetime
 @model_validator(mode="after")
 def valid_window(self):
  if (self.starts_at.tzinfo is None or self.starts_at.utcoffset() is None or
      self.ends_at.tzinfo is None or self.ends_at.utcoffset() is None or
      self.ends_at <= self.starts_at):
   raise ValueError("Campaign requires an ordered timezone-aware window")
  return self

@router.post("",status_code=201)
def create_campaign(body:CampaignDraft,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 cid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.campaigns
  (id,code,discount_bps,minimum_subtotal,maximum_discount,audience,starts_at,ends_at,created_by)
  VALUES (:id,:code,:bps,:minimum,:maximum,:audience,:start,:end,:actor)"""),
  {"id":cid,"code":body.code,"bps":body.discount_bps,"minimum":body.minimum_subtotal,
   "maximum":body.maximum_discount,"audience":body.audience,
   "start":body.starts_at,"end":body.ends_at,"actor":identity["sub"]})
  db.execute(text("""INSERT INTO marketing.campaign_events (id,campaign_id,actor_subject,action)
   VALUES (:id,:campaign,:actor,'created')"""),
   {"id":uuid4(),"campaign":cid,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback()
  raise HTTPException(409,"Campaign code already exists")
 return {"id":str(cid),"status":"draft","checkout_enabled":False}

@router.post("/{campaign_id}/approve")
def approve_campaign(campaign_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT status,created_by FROM marketing.campaigns
 WHERE id=:id FOR UPDATE"""),{"id":campaign_id}).mappings().first()
 if row is None:raise HTTPException(404,"Campaign not found")
 if row["status"]!="draft":raise HTTPException(409,"Only draft campaigns may be approved")
 if row["created_by"]==identity["sub"]:raise HTTPException(403,"Creator cannot approve campaign")
 db.execute(text("""UPDATE marketing.campaigns SET status='approved',approved_by=:actor WHERE id=:id"""),
  {"id":campaign_id,"actor":identity["sub"]})
 db.execute(text("""INSERT INTO marketing.campaign_events (id,campaign_id,actor_subject,action)
 VALUES (:id,:campaign,:actor,'approved')"""),
  {"id":uuid4(),"campaign":campaign_id,"actor":identity["sub"]})
 db.commit()
 return {"id":str(campaign_id),"status":"approved","checkout_enabled":False}

@router.get("")
def list_campaigns(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,code,discount_bps,minimum_subtotal,maximum_discount,
 audience,starts_at,ends_at,status,created_by,approved_by
 FROM marketing.campaigns ORDER BY created_at DESC LIMIT 200""")).mappings().all()
 return [dict(row) for row in rows]

@router.post("/{campaign_id}/disable")
def disable_campaign(campaign_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT status FROM marketing.campaigns
 WHERE id=:id FOR UPDATE"""),{"id":campaign_id}).mappings().first()
 if row is None:raise HTTPException(404,"Campaign not found")
 if row["status"]=="disabled":raise HTTPException(409,"Campaign already disabled")
 db.execute(text("UPDATE marketing.campaigns SET status='disabled' WHERE id=:id"),{"id":campaign_id})
 db.execute(text("""INSERT INTO marketing.campaign_events (id,campaign_id,actor_subject,action)
 VALUES (:id,:campaign,:actor,'disabled')"""),
 {"id":uuid4(),"campaign":campaign_id,"actor":identity["sub"]})
 db.commit()
 return {"id":str(campaign_id),"status":"disabled","checkout_enabled":False}

@router.get("/{campaign_id}/events")
def campaign_events(campaign_id:UUID,identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 exists=db.execute(text("SELECT id FROM marketing.campaigns WHERE id=:id"),{"id":campaign_id}).mappings().first()
 if not exists:raise HTTPException(404,"Campaign not found")
 rows=db.execute(text("""SELECT id,actor_subject,action,created_at FROM marketing.campaign_events
 WHERE campaign_id=:id ORDER BY created_at,id LIMIT 500"""),{"id":campaign_id}).mappings().all()
 return [dict(row) for row in rows]

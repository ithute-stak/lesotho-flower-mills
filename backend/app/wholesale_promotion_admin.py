"""Non-payable wholesale promotion tiers with independent approval."""
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import db_session
from .finance_permissions import finance_read,finance_review,finance_admin

router=APIRouter(prefix="/api/v1/admin/wholesale-promotions",tags=["wholesale-promotions"])
class WholesaleTierDraft(BaseModel):
 campaign_id:UUID
 product_id:UUID
 minimum_quantity:int=Field(ge=2,le=1000000)
 discount_bps:int=Field(ge=1,le=10000)

@router.post("",status_code=201)
def create_wholesale_tier(body:WholesaleTierDraft,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 campaign=db.execute(text("SELECT status,audience FROM marketing.campaigns WHERE id=:id FOR UPDATE"),
  {"id":body.campaign_id}).mappings().first()
 if campaign is None:raise HTTPException(404,"Campaign not found")
 if campaign["audience"]!="business" or campaign["status"]=="disabled":
  raise HTTPException(409,"An enabled business campaign is required")
 tier_id=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.wholesale_discount_tiers
  (id,campaign_id,product_id,minimum_quantity,discount_bps,created_by)
  VALUES (:id,:campaign,:product,:quantity,:discount,:actor)"""),
  {"id":tier_id,"campaign":body.campaign_id,"product":body.product_id,
   "quantity":body.minimum_quantity,"discount":body.discount_bps,"actor":identity["sub"]})
  db.execute(text("""INSERT INTO marketing.wholesale_tier_events (id,tier_id,actor_subject,action)
  VALUES (:id,:tier,:actor,'created')"""),{"id":uuid4(),"tier":tier_id,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Quantity break already configured or invalid product")
 return {"id":str(tier_id),"status":"draft","checkout_enabled":False}

@router.post("/{tier_id}/approve")
def approve_wholesale_tier(tier_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT t.status,t.created_by,c.status AS campaign_status,c.audience
 FROM marketing.wholesale_discount_tiers t JOIN marketing.campaigns c ON c.id=t.campaign_id
 WHERE t.id=:id FOR UPDATE OF t"""),{"id":tier_id}).mappings().first()
 if row is None:raise HTTPException(404,"Wholesale tier not found")
 if row["status"]!="draft" or row["campaign_status"]=="disabled" or row["audience"]!="business":
  raise HTTPException(409,"Tier or campaign is not eligible for approval")
 if row["created_by"]==identity["sub"]:raise HTTPException(403,"Creator cannot approve own tier")
 db.execute(text("""UPDATE marketing.wholesale_discount_tiers
 SET status='approved',approved_by=:actor WHERE id=:id"""),{"id":tier_id,"actor":identity["sub"]})
 db.execute(text("""INSERT INTO marketing.wholesale_tier_events (id,tier_id,actor_subject,action)
 VALUES (:id,:tier,:actor,'approved')"""),{"id":uuid4(),"tier":tier_id,"actor":identity["sub"]})
 db.commit()
 return {"id":str(tier_id),"status":"approved","checkout_enabled":False}

@router.get("")
def list_wholesale_tiers(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,campaign_id,product_id,minimum_quantity,discount_bps,status,
 created_by,approved_by,created_at FROM marketing.wholesale_discount_tiers
 ORDER BY created_at DESC LIMIT 200""")).mappings().all()
 return [dict(row) for row in rows]

@router.post("/{tier_id}/disable")
def disable_wholesale_tier(tier_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("SELECT status FROM marketing.wholesale_discount_tiers WHERE id=:id FOR UPDATE"),{"id":tier_id}).mappings().first()
 if row is None:raise HTTPException(404,"Wholesale tier not found")
 if row["status"]=="disabled":raise HTTPException(409,"Wholesale tier already disabled")
 db.execute(text("UPDATE marketing.wholesale_discount_tiers SET status='disabled' WHERE id=:id"),{"id":tier_id})
 db.execute(text("""INSERT INTO marketing.wholesale_tier_events (id,tier_id,actor_subject,action)
 VALUES (:id,:tier,:actor,'disabled')"""),{"id":uuid4(),"tier":tier_id,"actor":identity["sub"]})
 db.commit()
 return {"id":str(tier_id),"status":"disabled","checkout_enabled":False}

@router.get("/{tier_id}/events")
def wholesale_tier_events(tier_id:UUID,identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 exists=db.execute(text("SELECT id FROM marketing.wholesale_discount_tiers WHERE id=:id"),{"id":tier_id}).mappings().first()
 if exists is None:raise HTTPException(404,"Wholesale tier not found")
 rows=db.execute(text("""SELECT id,actor_subject,action,created_at FROM marketing.wholesale_tier_events
 WHERE tier_id=:id ORDER BY created_at,id LIMIT 500"""),{"id":tier_id}).mappings().all()
 return [dict(row) for row in rows]

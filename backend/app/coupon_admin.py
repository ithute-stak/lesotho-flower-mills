"""Restricted coupon inventory endpoints; coupons cannot be redeemed."""
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import db_session
from .finance_permissions import finance_read,finance_review,finance_admin

router=APIRouter(prefix="/api/v1/admin/coupons",tags=["coupons"])

class NewCoupon(BaseModel):
 campaign_id:UUID
 code:str=Field(min_length=4,max_length=64,pattern=r"^[A-Z0-9_-]+$")
 max_redemptions:int=Field(ge=1,le=1000000)

@router.post("",status_code=201)
def create_coupon(body:NewCoupon,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 row=db.execute(text("SELECT status FROM marketing.campaigns WHERE id=:id FOR UPDATE"),{"id":body.campaign_id}).mappings().first()
 if row is None:raise HTTPException(404,"Campaign not found")
 if row["status"]=="disabled":raise HTTPException(409,"Campaign disabled")
 cid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.coupons (id,campaign_id,code,max_redemptions,created_by)
  VALUES (:id,:campaign,:code,:limit,:actor)"""),
  {"id":cid,"campaign":body.campaign_id,"code":body.code,"limit":body.max_redemptions,"actor":identity["sub"]})
  db.execute(text("""INSERT INTO marketing.coupon_events (id,coupon_id,actor_subject,action)
  VALUES (:id,:coupon,:actor,'created')"""),{"id":uuid4(),"coupon":cid,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback()
  raise HTTPException(409,"Coupon code already exists")
 return {"id":str(cid),"status":"draft","redeemable":False}

@router.get("")
def list_coupons(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,campaign_id,code,max_redemptions,redemption_count,
 status,created_by,created_at FROM marketing.coupons ORDER BY created_at DESC LIMIT 200""")).mappings().all()
 return [dict(row) for row in rows]

@router.post("/{coupon_id}/disable")
def disable_coupon(coupon_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("SELECT status FROM marketing.coupons WHERE id=:id FOR UPDATE"),{"id":coupon_id}).mappings().first()
 if not row:raise HTTPException(404,"Coupon not found")
 if row["status"]=="disabled":raise HTTPException(409,"Coupon already disabled")
 db.execute(text("UPDATE marketing.coupons SET status='disabled' WHERE id=:id"),{"id":coupon_id})
 db.execute(text("""INSERT INTO marketing.coupon_events (id,coupon_id,actor_subject,action)
 VALUES (:id,:coupon,:actor,'disabled')"""),{"id":uuid4(),"coupon":coupon_id,"actor":identity["sub"]})
 db.commit()
 return {"id":str(coupon_id),"status":"disabled","redeemable":False}

@router.get("/{coupon_id}/events")
def coupon_events(coupon_id:UUID,identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 exists=db.execute(text("SELECT id FROM marketing.coupons WHERE id=:id"),{"id":coupon_id}).mappings().first()
 if not exists:raise HTTPException(404,"Coupon not found")
 rows=db.execute(text("""SELECT id,actor_subject,action,created_at
 FROM marketing.coupon_events WHERE coupon_id=:id ORDER BY created_at,id LIMIT 500"""),
 {"id":coupon_id}).mappings().all()
 return [dict(row) for row in rows]

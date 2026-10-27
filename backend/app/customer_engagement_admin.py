"""Internal customer engagement drafts; no loyalty credits or scheduled orders."""
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import db_session
from .finance_permissions import finance_read,finance_review
router=APIRouter(prefix="/api/v1/admin/customer-engagement",tags=["customer-engagement"])

class LoyaltyDraft(BaseModel):
 customer_id:UUID

class RepeatOrderDraft(BaseModel):
 customer_id:UUID
 product_id:UUID
 quantity:int=Field(ge=1,le=1000000)
 frequency:str=Field(pattern="^(weekly|monthly)$")

class CancelRepeatOrder(BaseModel):
 reason:str=Field(min_length=5,max_length=500)

class ReferralDraft(BaseModel):
 referrer_customer_id:UUID
 referred_customer_id:UUID

@router.post("/referrals",status_code=201)
def create_referral_draft(body:ReferralDraft,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 if body.referrer_customer_id==body.referred_customer_id:
  raise HTTPException(422,"Self-referrals are not permitted")
 rid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.referral_plans
  (id,referrer_customer_id,referred_customer_id,created_by)
  VALUES (:id,:referrer,:referred,:actor)"""),
  {"id":rid,"referrer":body.referrer_customer_id,
   "referred":body.referred_customer_id,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Duplicate referral or invalid customer")
 return {"id":str(rid),"status":"draft","rewards_enabled":False}

@router.get("/referrals")
def list_referral_drafts(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,referrer_customer_id,referred_customer_id,status,created_by,created_at
 FROM marketing.referral_plans ORDER BY created_at DESC LIMIT 200""")).mappings().all()
 return [dict(r) for r in rows]

@router.get("/repeat-orders")
def list_repeat_orders(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,customer_id,product_id,quantity,frequency,status,created_by,created_at,cancelled_by,cancelled_at,cancellation_reason
 FROM marketing.repeat_order_templates ORDER BY created_at DESC,id DESC LIMIT 200""")).mappings().all()
 return [dict(row) for row in rows]

@router.post("/repeat-orders/{template_id}/cancel")
def cancel_repeat_order(template_id:UUID,body:CancelRepeatOrder,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 row=db.execute(text("""UPDATE marketing.repeat_order_templates
 SET status='cancelled',cancelled_by=:actor,cancelled_at=now(),cancellation_reason=:reason
 WHERE id=:id AND status='draft' RETURNING id"""),
 {"id":template_id,"actor":identity["sub"],"reason":body.reason.strip()}).first()
 if row is None:
  db.rollback()
  raise HTTPException(409,"Template is not a draft or does not exist")
 db.commit()
 return {"id":str(template_id),"status":"cancelled","automatic_ordering_enabled":False}

@router.post("/loyalty",status_code=201)
def create_loyalty_draft(body:LoyaltyDraft,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 eid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.loyalty_enrolments (id,customer_id,created_by)
  VALUES (:id,:customer,:actor)"""),{"id":eid,"customer":body.customer_id,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Customer already enrolled in a draft or customer not found")
 return {"id":str(eid),"status":"draft","points_enabled":False}

@router.post("/repeat-orders",status_code=201)
def create_repeat_order_draft(body:RepeatOrderDraft,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 tid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.repeat_order_templates
  (id,customer_id,product_id,quantity,frequency,created_by)
  VALUES (:id,:customer,:product,:quantity,:frequency,:actor)"""),
  {"id":tid,"customer":body.customer_id,"product":body.product_id,
   "quantity":body.quantity,"frequency":body.frequency,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Customer or product not found")
 return {"id":str(tid),"status":"draft","automatic_ordering_enabled":False}

@router.get("/summary")
def customer_engagement_summary(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 loyalty=db.execute(text("SELECT COUNT(*) FROM marketing.loyalty_enrolments")).scalar_one()
 repeat=db.execute(text("SELECT COUNT(*) FROM marketing.repeat_order_templates WHERE status='draft'")).scalar_one()
 cancelled=db.execute(text("SELECT COUNT(*) FROM marketing.repeat_order_templates WHERE status='cancelled'")).scalar_one()
 referrals=db.execute(text("SELECT COUNT(*) FROM marketing.referral_plans")).scalar_one()
 return {"draft_loyalty_enrolments":loyalty,"draft_repeat_order_templates":repeat,"cancelled_repeat_order_templates":cancelled,"draft_referrals":referrals,
 "points_enabled":False,"automatic_ordering_enabled":False,"referral_rewards_enabled":False}

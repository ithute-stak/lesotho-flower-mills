"""Independent review of financial totals, disabled for live approval pending policy validation."""
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import finance_identity
from .db import db_session
router=APIRouter(prefix="/api/v1/admin/final-total-approval",tags=["final-total-approval"])

@router.get("/{order_id}/audit")
def audit(order_id:UUID,identity:dict=Depends(finance_identity),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT actor_subject,action,total_amount,policy_reference,created_at
 FROM finance.total_review_events WHERE sales_order_id=:id ORDER BY created_at"""),{"id":order_id}).mappings().all()
 return [dict(r) for r in rows]

@router.post("/{order_id}/approve")
def approve(order_id:UUID,identity:dict=Depends(finance_identity),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT created_by,review_status FROM finance.order_totals
 WHERE sales_order_id=:id FOR UPDATE"""),{"id":order_id}).mappings().first()
 if not row:raise HTTPException(404,"No order total exists")
 if row["review_status"]!="draft":raise HTTPException(409,"Only draft totals can be reviewed")
 if row["created_by"]==identity["sub"]:raise HTTPException(403,"Maker cannot approve their own total")
 # Existing JWT roles and policy snapshots are not independently verified.
 # Fail closed: do not allow staff to approve a payable amount yet.
 raise HTTPException(409,"Final approval disabled until validated tax policy, tariff snapshots and central role verification exist")

@router.get("/{order_id}/readiness")
def readiness(order_id:UUID,identity:dict=Depends(finance_identity),db:Session=Depends(db_session)):
 from .financial_readiness import assess
 order=db.execute(text("SELECT status FROM sales.sales_orders WHERE id=:id"),{"id":order_id}).mappings().first()
 if not order:raise HTTPException(404,"Order not found")
 total=db.execute(text("""SELECT review_status,total,currency,policy_reference FROM finance.order_totals
 WHERE sales_order_id=:id"""),{"id":order_id}).mappings().first()
 # Policy lineage is not yet FK-bound; fail closed rather than assuming a text reference proves approval.
 check=db.execute(text("""SELECT amount,currency FROM finance.checkout_sessions
 WHERE sales_order_id=:id ORDER BY created_at DESC LIMIT 1"""),{"id":order_id}).mappings().first()
 result=assess(order,total,None,check)
 return {"ready":result.ready,"blockers":list(result.blockers),"financial_approval_enabled":False}

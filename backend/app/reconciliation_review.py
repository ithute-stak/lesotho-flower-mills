"""Read-only finance investigation queue; no payment retry or manual paid switch."""
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .db import db_session
router=APIRouter(prefix="/api/v1/admin/reconciliation",tags=["payment-investigations"])

@router.get("/queue")
def queue(identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT a.id,a.sales_order_id,a.state,a.created_at,a.updated_at,
 o.order_number,a.amount,a.currency,
 (SELECT MAX(e.created_at) FROM finance.reconciliation_events e
  WHERE e.checkout_attempt_id=a.id) AS last_reviewed_at
 FROM finance.checkout_attempts a
 JOIN sales.sales_orders o ON o.id=a.sales_order_id
 WHERE a.state IN ('initiating','reconciliation_required')
 ORDER BY a.created_at ASC LIMIT 100""")).mappings().all()
 return [dict(row) for row in rows]

@router.get("/attempts/{attempt_id}/history")
def history(attempt_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 exists=db.execute(text("SELECT 1 FROM finance.checkout_attempts WHERE id=:id"),{"id":attempt_id}).first()
 if not exists:raise HTTPException(404,"Checkout attempt not found")
 rows=db.execute(text("""SELECT id,outcome,remote_status,actor,created_at
 FROM finance.reconciliation_events WHERE checkout_attempt_id=:id ORDER BY created_at"""),
 {"id":attempt_id}).mappings().all()
 return [dict(row) for row in rows]

"""Read-only driver self-service: assignments are scoped by signed-in identity."""
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from uuid import UUID
from .security import current_identity
from .db import db_session
router=APIRouter(prefix="/api/v1/driver",tags=["driver-portal"])

def driver_id(db:Session,subject:str):
    driver=db.execute(text("SELECT id FROM delivery.drivers WHERE identity_subject=:subject AND active=true"),
                      {"subject":subject}).mappings().first()
    if not driver:raise HTTPException(403,"Active driver account required")
    return driver["id"]

@router.get("/assignments")
def assigned_deliveries(identity:dict=Depends(current_identity),db:Session=Depends(db_session)):
    did=driver_id(db,identity["sub"])
    rows=db.execute(text("""SELECT a.id,a.status,a.created_at,
      so.order_number,v.registration AS vehicle_registration
      FROM delivery.assignments a
      JOIN sales.sales_orders so ON so.id=a.sales_order_id
      JOIN delivery.vehicles v ON v.id=a.vehicle_id
      WHERE a.driver_id=:driver ORDER BY a.created_at DESC LIMIT 100"""),
      {"driver":did}).mappings().all()
    return [dict(r) for r in rows]

@router.get("/assignments/{assignment_id}")
def assigned_detail(assignment_id:UUID,identity:dict=Depends(current_identity),db:Session=Depends(db_session)):
    did=driver_id(db,identity["sub"])
    row=db.execute(text("""SELECT a.id,a.status,a.created_at,
      so.order_number,v.registration AS vehicle_registration
      FROM delivery.assignments a
      JOIN sales.sales_orders so ON so.id=a.sales_order_id
      JOIN delivery.vehicles v ON v.id=a.vehicle_id
      WHERE a.id=:id AND a.driver_id=:driver"""),{"id":assignment_id,"driver":did}).mappings().first()
    if not row:raise HTTPException(404,"Assignment not found")
    return dict(row)

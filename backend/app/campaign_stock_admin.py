"""Read-only stock availability comparison and draft promotion plans."""
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import db_session
from .finance_permissions import finance_read,finance_review

router=APIRouter(prefix="/api/v1/admin/campaign-stock",tags=["campaign-stock"])
class StockPlan(BaseModel):
 campaign_id:UUID
 warehouse_id:UUID
 product_id:UUID
 planned_quantity:int=Field(ge=1,le=1000000)

@router.post("",status_code=201)
def create_stock_plan(body:StockPlan,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 campaign=db.execute(text("SELECT status FROM marketing.campaigns WHERE id=:id FOR UPDATE"),
  {"id":body.campaign_id}).mappings().first()
 if campaign is None:raise HTTPException(404,"Campaign not found")
 if campaign["status"]=="disabled":raise HTTPException(409,"Campaign disabled")
 balance=db.execute(text("""SELECT on_hand,reserved FROM inventory.stock_balances
 WHERE warehouse_id=:warehouse AND product_id=:product"""),
 {"warehouse":body.warehouse_id,"product":body.product_id}).mappings().first()
 if not balance:raise HTTPException(409,"No stock balance available for planning")
 available=balance["on_hand"]-balance["reserved"]
 if available<body.planned_quantity:raise HTTPException(409,"Planned quantity exceeds currently available stock")
 pid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.campaign_stock_plans
   (id,campaign_id,warehouse_id,product_id,planned_quantity,created_by)
   VALUES (:id,:campaign,:warehouse,:product,:quantity,:actor)"""),
   {"id":pid,"campaign":body.campaign_id,"warehouse":body.warehouse_id,
    "product":body.product_id,"quantity":body.planned_quantity,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"A plan already exists for this campaign, warehouse and product")
 return {"id":str(pid),"status":"draft","reserved":False,"stock_at_check":available}

@router.get("")
def list_stock_plans(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT p.id,p.campaign_id,p.warehouse_id,p.product_id,p.planned_quantity,
 p.status,p.created_by,COALESCE(b.on_hand-b.reserved,0) AS available_now
 FROM marketing.campaign_stock_plans p LEFT JOIN inventory.stock_balances b
 ON b.warehouse_id=p.warehouse_id AND b.product_id=p.product_id
 ORDER BY p.created_at DESC LIMIT 200""")).mappings().all()
 return [{"id":str(row["id"]),"campaign_id":str(row["campaign_id"]),
 "warehouse_id":str(row["warehouse_id"]),"product_id":str(row["product_id"]),
 "planned_quantity":row["planned_quantity"],"status":row["status"],
 "created_by":row["created_by"],"available_now":row["available_now"],
 "reserved":False} for row in rows]

"""Atomic stock reservations; access requires staff authorisation."""
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .db import db_session

router = APIRouter(prefix="/api/v1/admin/inventory", tags=["inventory"])

class WarehouseInput(BaseModel):
    code: str = Field(min_length=2,max_length=40)
    name: str = Field(min_length=2,max_length=150)

class ReceiptInput(BaseModel):
    warehouse_id: UUID
    product_id: UUID
    quantity: int = Field(ge=1,le=1000000)

@router.post("/warehouses",status_code=201)
def create_warehouse(body:WarehouseInput, identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    from sqlalchemy.exc import IntegrityError
    wid=uuid4()
    try:
        db.execute(text("INSERT INTO inventory.warehouses(id,code,name) VALUES (:id,:code,:name)"),
                   {"id":wid,"code":body.code,"name":body.name})
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409,"Warehouse code conflict")
    return {"id":str(wid),"code":body.code}

@router.get("/balances")
def balances(identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    rows=db.execute(text("""SELECT warehouse_id,product_id,on_hand,reserved,on_hand-reserved AS available
      FROM inventory.stock_balances ORDER BY warehouse_id,product_id LIMIT 500""")).mappings().all()
    return [dict(row) for row in rows]

def reserve_quantity(db:Session,warehouse_id:UUID,product_id:UUID,qty:int)->bool:
    """One conditional UPDATE atomically rejects competing reservations."""
    if qty<=0:
        raise ValueError("Quantity must be positive")
    changed=db.execute(text("""UPDATE inventory.stock_balances SET reserved=reserved+:qty
      WHERE warehouse_id=:warehouse AND product_id=:product AND on_hand-reserved>=:qty"""),
      {"warehouse":warehouse_id,"product":product_id,"qty":qty})
    return changed.rowcount==1

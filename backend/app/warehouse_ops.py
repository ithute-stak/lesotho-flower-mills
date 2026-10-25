"""Audited stock transactions. Posting privileges are staff-only development controls.

Production needs warehouse-specific permissions and independent adjustment approval.
"""
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .authorization import staff_identity
from .db import db_session

router=APIRouter(prefix="/api/v1/admin/warehouse",tags=["warehouse-operations"])

class MovementRequest(BaseModel):
    operation_key: str=Field(min_length=8,max_length=128)
    warehouse_id: UUID
    product_id: UUID
    quantity: int=Field(ge=1,le=1000000)
    reference: str=Field(min_length=3,max_length=160)

class AdjustmentRequest(MovementRequest):
    direction: str

class TransferRequest(BaseModel):
    operation_key: str=Field(min_length=8,max_length=128)
    from_warehouse_id: UUID
    to_warehouse_id: UUID
    product_id: UUID
    quantity: int=Field(ge=1,le=1000000)
    reference: str=Field(min_length=3,max_length=160)

def claim(db:Session,key:str,actor:str,kind:str):
    try:
        db.execute(text("""INSERT INTO inventory.stock_operations(id,operation_key,operation_type,actor_id)
            VALUES (:id,:key,:kind,:actor)"""),{"id":uuid4(),"key":key,"kind":kind,"actor":actor})
    except IntegrityError:
        db.rollback()
        raise HTTPException(409,"Operation key already used")

def post(db:Session,warehouse:UUID,product:UUID,delta:int,kind:str,key:str,reference:str,actor:str):
    # The conditional update is the stock invariant: no reduction below reservations.
    db.execute(text("""INSERT INTO inventory.stock_balances(warehouse_id,product_id,on_hand,reserved)
        VALUES (:warehouse,:product,0,0) ON CONFLICT DO NOTHING"""),{"warehouse":warehouse,"product":product})
    result=db.execute(text("""UPDATE inventory.stock_balances SET on_hand=on_hand+:delta
      WHERE warehouse_id=:warehouse AND product_id=:product AND on_hand+:delta>=reserved
      AND on_hand+:delta>=0"""),{"warehouse":warehouse,"product":product,"delta":delta})
    if result.rowcount!=1:
        raise HTTPException(409,"Insufficient unreserved stock for movement")
    db.execute(text("""INSERT INTO inventory.stock_movements
      (id,operation_key,warehouse_id,product_id,delta,movement_type,reference,actor_id)
      VALUES (:id,:key,:warehouse,:product,:delta,:kind,:reference,:actor)"""),
      {"id":uuid4(),"key":key,"warehouse":warehouse,"product":product,"delta":delta,
       "kind":kind,"reference":reference,"actor":actor})

@router.post("/receipts",status_code=201)
def receipt(body:MovementRequest,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    try:
        claim(db,body.operation_key,identity["sub"],"receipt")
        post(db,body.warehouse_id,body.product_id,body.quantity,"receipt",body.operation_key,body.reference,identity["sub"])
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"status":"posted","quantity_received":body.quantity}

@router.post("/adjustments",status_code=201)
def adjustment(body:AdjustmentRequest,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    if body.direction not in {"increase","decrease"}:
        raise HTTPException(422,"Direction must be increase or decrease")
    delta=body.quantity if body.direction=="increase" else -body.quantity
    try:
        claim(db,body.operation_key,identity["sub"],"adjustment")
        post(db,body.warehouse_id,body.product_id,delta,"adjustment",body.operation_key,body.reference,identity["sub"])
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"status":"posted","delta":delta}

@router.post("/transfers",status_code=201)
def transfer(body:TransferRequest,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    if body.from_warehouse_id==body.to_warehouse_id:
        raise HTTPException(422,"Transfer needs distinct warehouses")
    try:
        claim(db,body.operation_key,identity["sub"],"transfer")
        # Deterministic warehouse ordering avoids deadlocks under opposing transfers.
        movements=[(body.from_warehouse_id,-body.quantity,"transfer_out"),
                   (body.to_warehouse_id,body.quantity,"transfer_in")]
        for warehouse,delta,kind in sorted(movements,key=lambda m:str(m[0])):
            post(db,warehouse,body.product_id,delta,kind,body.operation_key+":"+kind,body.reference,identity["sub"])
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"status":"posted","quantity_transferred":body.quantity}

@router.get("/movements")
def movements(identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    rows=db.execute(text("""SELECT id,operation_key,warehouse_id,product_id,delta,movement_type,
         reference,actor_id,created_at FROM inventory.stock_movements
         ORDER BY created_at DESC LIMIT 200""")).mappings().all()
    return [dict(r) for r in rows]

@router.post("/reservations/{reservation_id}/release")
def release_reservation(reservation_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    """Release an active reservation atomically; prevents duplicate release."""
    row=db.execute(text("""SELECT warehouse_id,product_id,quantity,status
      FROM inventory.stock_reservations WHERE id=:id FOR UPDATE"""),
      {"id":reservation_id}).mappings().first()
    if not row:
        raise HTTPException(404,"Reservation not found")
    if row["status"]!="active":
        raise HTTPException(409,"Reservation is not active")
    updated=db.execute(text("""UPDATE inventory.stock_balances SET reserved=reserved-:quantity
      WHERE warehouse_id=:warehouse AND product_id=:product AND reserved>=:quantity"""),
      {"warehouse":row["warehouse_id"],"product":row["product_id"],"quantity":row["quantity"]})
    if updated.rowcount!=1:
        db.rollback()
        raise HTTPException(409,"Stock balance does not match reservation")
    result=db.execute(text("""UPDATE inventory.stock_reservations SET status='released'
      WHERE id=:id AND status='active'"""),{"id":reservation_id})
    if result.rowcount!=1:
        db.rollback()
        raise HTTPException(409,"Reservation already processed")
    db.commit()
    return {"id":str(reservation_id),"status":"released"}

"""Warehouse picking and loading verification; no dispatch while payment is pending."""
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .db import db_session

router=APIRouter(prefix="/api/v1/admin/fulfilment",tags=["fulfilment"])

class PickLine(BaseModel):
    item_id:UUID
    quantity:int=Field(ge=1)

class PickConfirm(BaseModel):
    items:list[PickLine]=Field(min_length=1,max_length=100)

class LoadRequest(BaseModel):
    vehicle_registration:str=Field(min_length=2,max_length=40)
    driver_name:str=Field(min_length=2,max_length=150)
    items:list[PickLine]=Field(min_length=1,max_length=100)

@router.post("/orders/{order_id}/pick-list",status_code=201)
def create_pick_list(order_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    order=db.execute(text("""SELECT id,status,quotation_id FROM sales.sales_orders WHERE id=:id FOR UPDATE"""),{"id":order_id}).mappings().first()
    if not order:raise HTTPException(404,"Order not found")
    if order["status"]!="confirmed":
        raise HTTPException(409,"Order must be payment/credit confirmed before picking")
    if db.execute(text("SELECT 1 FROM fulfilment.pick_lists WHERE sales_order_id=:id"),{"id":order_id}).first():
        raise HTTPException(409,"Pick list already exists")
    reservations=db.execute(text("""SELECT qi.id AS item_id,qi.quantity FROM sales.quotation_items qi
        JOIN inventory.stock_reservations sr ON sr.quotation_item_id=qi.id
        WHERE qi.quotation_id=:quote AND sr.status='active' ORDER BY qi.id"""),{"quote":order["quotation_id"]}).mappings().all()
    if not reservations:raise HTTPException(409,"No active reserved stock")
    pid=uuid4()
    db.execute(text("INSERT INTO fulfilment.pick_lists(id,sales_order_id,created_by) VALUES (:id,:order,:actor)"),
               {"id":pid,"order":order_id,"actor":identity["sub"]})
    for row in reservations:
        db.execute(text("""INSERT INTO fulfilment.pick_items(id,pick_list_id,quotation_item_id,required_qty)
          VALUES (:id,:pick,:item,:qty)"""),{"id":uuid4(),"pick":pid,"item":row["item_id"],"qty":row["quantity"]})
    db.commit()
    return {"id":str(pid),"status":"pending","item_count":len(reservations)}

@router.post("/pick-lists/{pick_id}/confirm")
def confirm_pick(pick_id:UUID,body:PickConfirm,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    pick=db.execute(text("SELECT status FROM fulfilment.pick_lists WHERE id=:id FOR UPDATE"),{"id":pick_id}).mappings().first()
    if not pick:raise HTTPException(404,"Pick list not found")
    if pick["status"]!="pending":raise HTTPException(409,"Pick list already processed")
    items=db.execute(text("SELECT id,required_qty FROM fulfilment.pick_items WHERE pick_list_id=:id"),{"id":pick_id}).mappings().all()
    expected={str(r["id"]):r["required_qty"] for r in items}
    provided={str(r.item_id):r.quantity for r in body.items}
    if len(provided)!=len(body.items) or provided!=expected:
        raise HTTPException(422,"Every line must be picked in its full reserved quantity")
    for entry in body.items:
        db.execute(text("UPDATE fulfilment.pick_items SET picked_qty=:qty WHERE id=:id"),
          {"id":entry.item_id,"qty":entry.quantity})
    db.execute(text("UPDATE fulfilment.pick_lists SET status='picked' WHERE id=:id"),{"id":pick_id})
    db.commit()
    return {"id":str(pick_id),"status":"picked"}

@router.post("/pick-lists/{pick_id}/loading",status_code=201)
def confirm_loading(pick_id:UUID,body:LoadRequest,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    pick=db.execute(text("""SELECT pl.status,so.status AS order_status FROM fulfilment.pick_lists pl
      JOIN sales.sales_orders so ON so.id=pl.sales_order_id WHERE pl.id=:id FOR UPDATE OF pl,so"""),
      {"id":pick_id}).mappings().first()
    if not pick:raise HTTPException(404,"Pick list not found")
    if pick["status"]!="picked" or pick["order_status"]!="confirmed":
        raise HTTPException(409,"Picking and order confirmation required")
    if db.execute(text("SELECT 1 FROM fulfilment.loading_manifests WHERE pick_list_id=:id"),{"id":pick_id}).first():
        raise HTTPException(409,"Loading manifest already exists")
    items=db.execute(text("SELECT id,picked_qty FROM fulfilment.pick_items WHERE pick_list_id=:id"),{"id":pick_id}).mappings().all()
    expected={str(r["id"]):r["picked_qty"] for r in items}
    provided={str(r.item_id):r.quantity for r in body.items}
    if len(provided)!=len(body.items) or provided!=expected:
        raise HTTPException(422,"Loading quantities must match picked quantities")
    mid=uuid4()
    db.execute(text("""INSERT INTO fulfilment.loading_manifests
      (id,pick_list_id,vehicle_registration,driver_name,status,verified_by,verified_at)
      VALUES (:id,:pick,:vehicle,:driver,'verified',:actor,now())"""),
      {"id":mid,"pick":pick_id,"vehicle":body.vehicle_registration,"driver":body.driver_name,"actor":identity["sub"]})
    for entry in body.items:
        db.execute(text("""INSERT INTO fulfilment.loading_items(id,manifest_id,pick_item_id,loaded_qty)
           VALUES (:id,:manifest,:item,:quantity)"""),
           {"id":uuid4(),"manifest":mid,"item":entry.item_id,"quantity":entry.quantity})
    db.commit()
    return {"id":str(mid),"status":"verified","dispatch_status":"not_dispatched"}

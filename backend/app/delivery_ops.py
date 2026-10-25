"""Controlled delivery allocation; dispatch remains disabled until settlement integration."""
from uuid import UUID,uuid4
from decimal import Decimal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .authorization import staff_identity
from .db import db_session
router=APIRouter(prefix="/api/v1/admin/delivery",tags=["delivery"])
class DriverCreate(BaseModel):
 identity_subject:str=Field(min_length=2,max_length=255)
 display_name:str=Field(min_length=2,max_length=150)
class VehicleCreate(BaseModel):
 registration:str=Field(min_length=2,max_length=40)
class Assign(BaseModel):
 order_id:UUID
 driver_id:UUID
 vehicle_id:UUID
class Position(BaseModel):
 latitude:Decimal=Field(ge=-90,le=90)
 longitude:Decimal=Field(ge=-180,le=180)
@router.post("/drivers",status_code=201)
def add_driver(body:DriverCreate,actor:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 ident=uuid4()
 try:
  db.execute(text("INSERT INTO delivery.drivers(id,identity_subject,display_name) VALUES (:id,:subject,:name)"),{"id":ident,"subject":body.identity_subject,"name":body.display_name});db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Driver account already registered")
 return {"id":str(ident),"display_name":body.display_name}
@router.post("/vehicles",status_code=201)
def add_vehicle(body:VehicleCreate,actor:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 ident=uuid4()
 try:
  db.execute(text("INSERT INTO delivery.vehicles(id,registration) VALUES (:id,:reg)"),{"id":ident,"reg":body.registration});db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Vehicle registration already exists")
 return {"id":str(ident),"registration":body.registration}
@router.post("/assignments",status_code=201)
def create_assignment(body:Assign,actor:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 order=db.execute(text("SELECT status FROM sales.sales_orders WHERE id=:id FOR UPDATE"),{"id":body.order_id}).mappings().first()
 if not order:raise HTTPException(404,"Order not found")
 if order["status"]!="confirmed":raise HTTPException(409,"Order must be confirmed before assigning delivery")
 manifest=db.execute(text("""SELECT lm.status,lm.vehicle_registration FROM fulfilment.loading_manifests lm
 JOIN fulfilment.pick_lists pl ON pl.id=lm.pick_list_id WHERE pl.sales_order_id=:order"""),{"order":body.order_id}).mappings().first()
 if not manifest or manifest["status"]!="verified":raise HTTPException(409,"Verified loading manifest required")
 vehicle=db.execute(text("SELECT registration FROM delivery.vehicles WHERE id=:id AND active=true"),{"id":body.vehicle_id}).mappings().first()
 driver=db.execute(text("SELECT id FROM delivery.drivers WHERE id=:id AND active=true"),{"id":body.driver_id}).first()
 if not vehicle or not driver:raise HTTPException(422,"Active driver and vehicle required")
 if vehicle["registration"]!=manifest["vehicle_registration"]:raise HTTPException(409,"Assigned vehicle does not match loading manifest")
 ident=uuid4()
 try:
  db.execute(text("""INSERT INTO delivery.assignments(id,sales_order_id,driver_id,vehicle_id,created_by)
 VALUES (:id,:order,:driver,:vehicle,:actor)"""),{"id":ident,"order":body.order_id,"driver":body.driver_id,"vehicle":body.vehicle_id,"actor":actor["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Order already has a delivery assignment")
 return {"id":str(ident),"status":"assigned","dispatched":False}
@router.get("/assignments/{assignment_id}")
def assignment_detail(assignment_id:UUID,actor:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 row=db.execute(text("SELECT * FROM delivery.assignments WHERE id=:id"),{"id":assignment_id}).mappings().first()
 if not row:raise HTTPException(404,"Assignment not found")
 return dict(row)
@router.post("/assignments/{assignment_id}/dispatch")
def dispatch(assignment_id:UUID,actor:dict=Depends(staff_identity)):
 raise HTTPException(409,"Dispatch disabled until confirmed payment, stock consumption and custody controls are available")
@router.get("/assignments/{assignment_id}/events")
def events(assignment_id:UUID,actor:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 records=db.execute(text("SELECT event_type,created_at,latitude,longitude FROM delivery.events WHERE assignment_id=:id ORDER BY created_at"),{"id":assignment_id}).mappings().all()
 return [dict(r) for r in records]

"""Customer-owned delivery acknowledgement; gated by verified dispatch and handover."""
from uuid import UUID,uuid4
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .security import current_identity
from .db import db_session

router=APIRouter(prefix="/api/v1/my/deliveries",tags=["delivery-acknowledgement"])
class Discrepancy(BaseModel):
 quotation_item_id:UUID
 received_quantity:int=Field(ge=0)
 reason:str=Field(min_length=3,max_length=400)
class Acknowledgement(BaseModel):
 decision:Literal["accepted","partial","rejected"]
 remarks:str=Field(default="",max_length=1000)
 discrepancies:list[Discrepancy]=Field(default_factory=list,max_length=100)

@router.post("/{assignment_id}/acknowledge",status_code=201)
def acknowledge(assignment_id:UUID,body:Acknowledgement,identity:dict=Depends(current_identity),db:Session=Depends(db_session)):
 assignment=db.execute(text("""SELECT a.id,a.status,so.quotation_id,so.customer_id
 FROM delivery.assignments a JOIN sales.sales_orders so ON so.id=a.sales_order_id
 JOIN crm.customer_users cu ON cu.customer_id=so.customer_id
 WHERE a.id=:id AND cu.identity_subject=:subject AND cu.membership_role='owner'
 FOR UPDATE OF a"""),{"id":assignment_id,"subject":identity["sub"]}).mappings().first()
 if not assignment:raise HTTPException(404,"Customer delivery assignment not found")
 if assignment["status"]!="arrived":raise HTTPException(409,"Delivery must arrive before customer acknowledgement")
 verified=db.execute(text("""SELECT 1 FROM delivery.handover_events
 WHERE assignment_id=:id AND event_type='code_verified' LIMIT 1"""),{"id":assignment_id}).first()
 if not verified:raise HTTPException(409,"Verified handover code required")
 expected_rows=db.execute(text("""SELECT id,quantity FROM sales.quotation_items WHERE quotation_id=:quote"""),{"quote":assignment["quotation_id"]}).mappings().all()
 expected={str(r["id"]):r["quantity"] for r in expected_rows}
 provided={str(d.quotation_item_id):d for d in body.discrepancies}
 if len(provided)!=len(body.discrepancies) or any(k not in expected or v.received_quantity>=expected[k] for k,v in provided.items()):
  raise HTTPException(422,"Discrepancies must identify unique ordered items with quantities below ordered amount")
 if body.decision=="accepted" and provided:raise HTTPException(422,"Accepted delivery cannot contain shortages")
 if body.decision=="partial" and not provided:raise HTTPException(422,"Partial delivery needs a discrepancy")
 if body.decision=="rejected" and (len(provided)!=len(expected) or any(v.received_quantity!=0 for v in provided.values())):
  raise HTTPException(422,"Rejected delivery must record zero receipt for each item")
 aid=uuid4()
 try:
  db.execute(text("""INSERT INTO delivery.acknowledgements
    (id,assignment_id,customer_subject,decision,remarks)
    VALUES (:id,:assignment,:subject,:decision,:remarks)"""),
    {"id":aid,"assignment":assignment_id,"subject":identity["sub"],"decision":body.decision,"remarks":body.remarks})
  for key,item in provided.items():
   db.execute(text("""INSERT INTO delivery.discrepancies
    (id,acknowledgement_id,quotation_item_id,expected_quantity,received_quantity,reason)
    VALUES (:id,:ack,:item,:expected,:received,:reason)"""),
    {"id":uuid4(),"ack":aid,"item":item.quotation_item_id,"expected":expected[key],
     "received":item.received_quantity,"reason":item.reason})
  if body.decision!="accepted":
   db.execute(text("INSERT INTO delivery.disputes(id,acknowledgement_id) VALUES (:id,:ack)"),
    {"id":uuid4(),"ack":aid})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Acknowledgement already submitted")
 return {"id":str(aid),"decision":body.decision,"delivery_completed":False,"dispute_opened":body.decision!="accepted"}

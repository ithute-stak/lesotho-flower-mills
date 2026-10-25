"""Append-only review of uncertain email delivery; no retry/automatic state changes."""
from uuid import UUID,uuid4
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .db import db_session
router=APIRouter(prefix="/api/v1/admin/notification-incidents",tags=["notification-incidents"])
class Review(BaseModel):
 disposition:Literal["investigating","confirmed_sent","delivery_unverified"]
 note:str=Field(min_length=10,max_length=2000)

@router.post("/{outbox_id}/reviews",status_code=201)
def review(outbox_id:UUID,body:Review,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT state FROM finance.alert_outbox
 WHERE id=:id FOR UPDATE"""),{"id":outbox_id}).mappings().first()
 if not row:raise HTTPException(404,"Email outbox record not found")
 if row["state"] not in ("sending","uncertain","failed"):
  raise HTTPException(409,"Only interrupted or failed notifications can be investigated")
 audit_id=uuid4()
 db.execute(text("""INSERT INTO finance.alert_delivery_incidents
 (id,outbox_id,actor,disposition,note) VALUES (:id,:outbox,:actor,:disposition,:note)"""),
 {"id":audit_id,"outbox":outbox_id,"actor":identity["sub"],"disposition":body.disposition,"note":body.note})
 db.commit()
 return {"review_id":str(audit_id),"disposition":body.disposition,
         "delivery_retried":False,"outbox_state_unchanged":True}

@router.get("/{outbox_id}/reviews")
def reviews(outbox_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,actor,disposition,note,created_at
 FROM finance.alert_delivery_incidents WHERE outbox_id=:id ORDER BY created_at"""),
 {"id":outbox_id}).mappings().all()
 return [dict(r) for r in rows]

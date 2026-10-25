"""Proof-of-delivery challenge validation; fail closed before dispatch.

No OTP issuance until the independent dispatch/payment workflow exists.
"""
import hashlib,hmac,os,secrets
from datetime import datetime,timezone
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .security import current_identity
from .db import db_session
router=APIRouter(prefix="/api/v1/driver/handover",tags=["proof-of-delivery"])

def hash_code(secret:str,assignment_id:UUID,code:str)->str:
 return hmac.new(secret.encode(),(str(assignment_id)+":"+code).encode(),hashlib.sha256).hexdigest()

def valid_code(secret:str,assignment_id:UUID,code:str,digest:str)->bool:
 return hmac.compare_digest(hash_code(secret,assignment_id,code),digest)

class CodeSubmission(BaseModel):
 code:str=Field(pattern=r"^\d{6}$")

@router.post("/{assignment_id}/verify")
def verify_handover(assignment_id:UUID,body:CodeSubmission,identity:dict=Depends(current_identity),db:Session=Depends(db_session)):
 driver=db.execute(text("SELECT id FROM delivery.drivers WHERE identity_subject=:subject AND active=true"),
  {"subject":identity["sub"]}).mappings().first()
 if not driver:raise HTTPException(403,"Active driver required")
 assignment=db.execute(text("SELECT status FROM delivery.assignments WHERE id=:id AND driver_id=:driver FOR UPDATE"),
  {"id":assignment_id,"driver":driver["id"]}).mappings().first()
 if not assignment:raise HTTPException(404,"Assignment not found")
 if assignment["status"]!="arrived":
  raise HTTPException(409,"Handover requires a dispatched, arrived delivery")
 secret=os.getenv("POD_HMAC_SECRET")
 if not secret or len(secret)<32:raise HTTPException(503,"Proof-of-delivery secret is not configured")
 challenge=db.execute(text("""SELECT code_hash,expires_at,attempts,consumed_at FROM delivery.handover_challenges
 WHERE assignment_id=:id FOR UPDATE"""),{"id":assignment_id}).mappings().first()
 if not challenge or challenge["consumed_at"] or challenge["expires_at"]<=datetime.now(timezone.utc):
  raise HTTPException(409,"No active delivery challenge")
 if challenge["attempts"]>=5:raise HTTPException(429,"Maximum attempts exceeded")
 if not valid_code(secret,assignment_id,body.code,challenge["code_hash"]):
  db.execute(text("UPDATE delivery.handover_challenges SET attempts=attempts+1 WHERE assignment_id=:id"),{"id":assignment_id})
  db.commit()
  raise HTTPException(422,"Incorrect handover code")
 # Verification of a code is not equivalent to proof that customer accepted full goods.
 db.execute(text("UPDATE delivery.handover_challenges SET consumed_at=now() WHERE assignment_id=:id"),{"id":assignment_id})
 db.execute(text("""INSERT INTO delivery.handover_events(id,assignment_id,actor_subject,event_type)
 VALUES (gen_random_uuid(),:id,:subject,'code_verified')"""),{"id":assignment_id,"subject":identity["sub"]})
 db.commit()
 return {"code_verified":True,"delivery_completed":False,"customer_acknowledgement_required":True}

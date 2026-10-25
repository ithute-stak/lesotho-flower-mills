"""Request-time finance grant verification; JWT roles alone are insufficient."""
from fastapi import Depends,HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from .security import current_identity
from .db import db_session

def require_finance_grant(allowed:set[str]):
 def dependency(identity:dict=Depends(current_identity),db:Session=Depends(db_session))->dict:
  subject=identity.get("sub")
  # Until Ithute Auth verifies issuer and account membership, local non-admin
  # tokens cannot elevate themselves to sensitive finance access.
  if identity.get("role")!="admin" or not subject:
   raise HTTPException(403,"Verified finance administrator identity required")
  rows=db.execute(text("""SELECT role FROM finance.finance_role_grants
   WHERE identity_subject=:subject AND active=true AND revoked_at IS NULL"""),
   {"subject":subject}).scalars().all()
  if not any(role in allowed for role in rows):
   raise HTTPException(403,"Active finance permission required")
  return identity
 return dependency

finance_read=require_finance_grant({"finance_viewer","finance_reviewer","finance_admin"})
finance_review=require_finance_grant({"finance_reviewer","finance_admin"})
finance_admin=require_finance_grant({"finance_admin"})

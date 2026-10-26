"""Read-only active staff link check; does not trust token role claims."""
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

def resolve_central_staff(db:Session,issuer:str,subject:str)->dict:
 if not isinstance(issuer,str) or not isinstance(subject,str) or not issuer or not subject:
  raise HTTPException(403,"Staff identity not linked")
 row=db.execute(text("""SELECT u.id,u.role FROM identity.central_staff_links l
 JOIN identity.users u ON u.id=l.local_user_id
 WHERE l.issuer=:issuer AND l.central_subject=:subject
 AND l.active=true AND l.revoked_at IS NULL AND l.verified_at IS NOT NULL
 AND u.active=true AND u.role IN ('admin','sales_manager')"""),
 {"issuer":issuer,"subject":subject}).mappings().first()
 if not row:raise HTTPException(403,"Active verified LFM staff membership required")
 return {"sub":str(row["id"]),"role":row["role"]}

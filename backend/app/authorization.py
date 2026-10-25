"""Resolve staff authorisation before opening database connections."""
from fastapi import Depends,HTTPException
from .security import current_identity,require_staff

def staff_identity(identity:dict=Depends(current_identity))->dict:
 require_staff(identity)
 return identity

def finance_identity(identity:dict=Depends(current_identity))->dict:
 """Fail closed to administrator role until independent finance memberships exist."""
 if identity.get("role")!="admin":
  raise HTTPException(403,"Finance administrator authorisation required")
 return identity

"""Explicitly injected central identity verification pipeline. Not a public route.

Caller MUST validate JWT signature, issuer, audience, nonce, and live central
session independently; no unverified request fields can satisfy these inputs.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .central_staff_membership import resolve_central_staff
from .staff_attestation_policy import validate_attestation_match

def resolve_verified_central_staff(db:Session, *, verified_claims:dict,
                                   session_active:bool)->dict:
 if not session_active:
  raise HTTPException(403,"Central session inactive")
 issuer=verified_claims.get("iss")
 subject=verified_claims.get("sub")
 if not isinstance(issuer,str) or not isinstance(subject,str) or not issuer or not subject:
  raise HTTPException(403,"Verified central identity required")
 local=resolve_central_staff(db,issuer,subject)
 validate_attestation_match(link_issuer=issuer,link_subject=subject,
                            verified_issuer=issuer,verified_subject=subject,
                            central_session_active=session_active)
 return local

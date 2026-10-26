"""Attestation evidence is never accepted from an administrator-submitted assertion.

A future central Auth adapter must verify a live authenticated subject, session
revocation and the link's exact issuer+subject before calling this helper.
This module deliberately provides no general-purpose public API.
"""
from fastapi import HTTPException

def validate_attestation_match(*,link_issuer:str,link_subject:str,
                               verified_issuer:str,verified_subject:str,
                               central_session_active:bool)->None:
 if not central_session_active:
  raise HTTPException(403,"Active central session required")
 if not link_issuer or not link_subject or verified_issuer!=link_issuer or verified_subject!=link_subject:
  raise HTTPException(403,"Central identity does not match proposed staff link")

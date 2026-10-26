from unittest.mock import Mock
import pytest
from fastapi import HTTPException
from app.central_staff_membership import resolve_central_staff

def test_unlinked_subject_denied():
 db=Mock()
 db.execute.return_value.mappings.return_value.first.return_value=None
 with pytest.raises(HTTPException) as err:
  resolve_central_staff(db,"https://issuer.example","unlinked")
 assert err.value.status_code==403

def test_linked_staff_returns_local_identity():
 db=Mock()
 db.execute.return_value.mappings.return_value.first.return_value={"id":"user-1","role":"admin"}
 assert resolve_central_staff(db,"https://issuer.example","central-1")=={"sub":"user-1","role":"admin"}

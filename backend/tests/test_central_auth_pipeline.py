import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from app.central_auth_pipeline import resolve_verified_central_staff

def test_central_session_inactive_denied():
 db=Mock()
 with pytest.raises(HTTPException) as exc:
  resolve_verified_central_staff(db,verified_claims={"iss":"https://auth.example","sub":"user"},session_active=False)
 assert exc.value.status_code==403
 db.execute.assert_not_called()

def test_missing_membership_denied():
 db=Mock()
 db.execute.return_value.mappings.return_value.first.return_value=None
 with pytest.raises(HTTPException) as exc:
  resolve_verified_central_staff(db,verified_claims={"iss":"https://auth.example","sub":"missing"},session_active=True)
 assert exc.value.status_code==403

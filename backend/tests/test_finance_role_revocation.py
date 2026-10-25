"""Security checks for request-time finance grant evaluation."""
from unittest.mock import Mock
import pytest
from fastapi import HTTPException
from app.finance_permissions import finance_admin,finance_read

def db_with_roles(roles):
 db=Mock()
 db.execute.return_value.scalars.return_value.all.return_value=roles
 return db

def test_revoked_role_cannot_authorize_next_request():
 identity={"sub":"admin-subject","role":"admin"}
 assert finance_read(identity,db_with_roles(["finance_viewer"]))==identity
 with pytest.raises(HTTPException) as exc:
  finance_read(identity,db_with_roles([]))
 assert exc.value.status_code==403

def test_viewer_cannot_manage_grants():
 with pytest.raises(HTTPException) as exc:
  finance_admin({"sub":"admin-subject","role":"admin"},db_with_roles(["finance_viewer"]))
 assert exc.value.status_code==403

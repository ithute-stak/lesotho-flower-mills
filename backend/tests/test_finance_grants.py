from unittest.mock import Mock
import pytest
from fastapi import HTTPException
from app.finance_permissions import finance_read,finance_review

def fake_db(roles):
 db=Mock()
 db.execute.return_value.scalars.return_value.all.return_value=roles
 return db

def test_finance_grant_denies_unapproved_staff():
 with pytest.raises(HTTPException) as exc:
  finance_read({"sub":"sales","role":"sales_manager"},fake_db(["finance_admin"]))
 assert exc.value.status_code==403

def test_finance_role_missing_is_forbidden():
 with pytest.raises(HTTPException) as exc:
  finance_read({"sub":"admin","role":"admin"},fake_db([]))
 assert exc.value.status_code==403

def test_finance_viewer_cannot_write_review():
 with pytest.raises(HTTPException) as exc:
  finance_review({"sub":"admin","role":"admin"},fake_db(["finance_viewer"]))
 assert exc.value.status_code==403

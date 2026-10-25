import pytest
from fastapi import HTTPException
from app.authorization import finance_identity

def test_sales_staff_cannot_access_finance_reviews():
 with pytest.raises(HTTPException) as exc:
  finance_identity({"sub":"sales-1","role":"sales_manager"})
 assert exc.value.status_code==403

def test_customer_cannot_access_finance_reviews():
 with pytest.raises(HTTPException) as exc:
  finance_identity({"sub":"customer-1","role":"customer"})
 assert exc.value.status_code==403

def test_admin_identity_allowed():
 assert finance_identity({"sub":"admin-1","role":"admin"})["sub"]=="admin-1"

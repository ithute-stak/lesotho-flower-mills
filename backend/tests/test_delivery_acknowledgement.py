from fastapi.testclient import TestClient
from app.main import app
from app.delivery_acknowledgement import Acknowledgement
from pydantic import ValidationError
import pytest

def test_customer_acknowledgement_requires_authentication():
 r=TestClient(app).post("/api/v1/my/deliveries/00000000-0000-0000-0000-000000000001/acknowledge",json={"decision":"accepted"})
 assert r.status_code==401

def test_rejects_unknown_decision():
 with pytest.raises(ValidationError):
  Acknowledgement(decision="delivered")

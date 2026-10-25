from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.proof_of_delivery import hash_code,valid_code
def test_code_hashing():
 key="a"*40
 ident=UUID(int=1)
 digest=hash_code(key,ident,"123456")
 assert valid_code(key,ident,"123456",digest)
 assert not valid_code(key,ident,"123457",digest)
 assert not valid_code(key,UUID(int=2),"123456",digest)
def test_handover_requires_auth():
 r=TestClient(app).post("/api/v1/driver/handover/00000000-0000-0000-0000-000000000001/verify",json={"code":"123456"})
 assert r.status_code==401

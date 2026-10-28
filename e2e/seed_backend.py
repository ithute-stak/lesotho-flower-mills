"""CI-only synthetic staff fixture; refuse all non-test databases."""
import os
from uuid import uuid4
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
from app.security import hash_password
url=os.environ["DATABASE_URL"]
database_url=make_url(url)
if (os.environ.get("CI")!="true" or os.environ.get("LFM_E2E_SEED")!="true"
    or database_url.database!="lfm_test"
    or database_url.host not in {"localhost","127.0.0.1","::1"}):
 raise SystemExit("Refusing to seed outside disposable CI database")
engine=create_engine(url)
with engine.begin() as db:
 db.execute(text("""INSERT INTO identity.users(id,email,password_hash,role,active)
 VALUES(:id,'e2e-warehouse@example.invalid',:password,'admin',true)"""),
 {"id":uuid4(),"password":hash_password("e2e-synthetic-only-password")})
with engine.begin() as db:
 db.execute(text("""INSERT INTO identity.users(id,email,password_hash,role,active)
 VALUES(:id,'e2e-customer@example.invalid',:password,'customer',true)"""),
 {"id":uuid4(),"password":hash_password("e2e-customer-test-password")})
engine.dispose()

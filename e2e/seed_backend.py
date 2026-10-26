"""CI-only synthetic staff fixture; refuse all non-test databases."""
import os
from uuid import uuid4
from sqlalchemy import create_engine,text
from app.security import hash_password
url=os.environ["DATABASE_URL"]
if os.environ.get("CI")!="true" or "lfm_test" not in url or os.environ.get("LFM_E2E_SEED")!="true":
 raise SystemExit("Refusing to seed outside disposable CI database")
engine=create_engine(url)
with engine.begin() as db:
 db.execute(text("""INSERT INTO identity.users(id,email,password_hash,role,active)
 VALUES(:id,'e2e-warehouse@example.invalid',:password,'admin',true)"""),
 {"id":uuid4(),"password":hash_password("e2e-synthetic-only-password")})
engine.dispose()

"""Atomic one-time callback state claims; NEVER logs raw OAuth state."""
import hashlib
from datetime import datetime,timezone
from sqlalchemy import text
from sqlalchemy.orm import Session

def claim_oauth_state(db:Session,state:str,expires_at:datetime)->bool:
 if not isinstance(state,str) or not 20<=len(state)<=512:
  return False
 if expires_at.tzinfo is None or expires_at<=datetime.now(timezone.utc):
  return False
 digest=hashlib.sha256(state.encode("utf-8")).hexdigest()
 row=db.execute(text("""INSERT INTO oauth_state_claims(state_digest,expires_at)
 VALUES(:digest,:expires_at) ON CONFLICT (state_digest) DO NOTHING
 RETURNING state_digest"""),{"digest":digest,"expires_at":expires_at}).first()
 db.commit()
 return row is not None

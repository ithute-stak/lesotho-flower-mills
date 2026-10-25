"""One-shot delivery entrypoint. No background timer installed."""
import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .alert_delivery import deliver_one,configured

def main():
 if not configured():
  print(json.dumps({"enabled":False,"reason":"delivery_disabled"}))
  return
 url=os.getenv("DATABASE_URL")
 if not url:raise RuntimeError("DATABASE_URL required")
 engine=create_engine(url,pool_pre_ping=True)
 try:
  with Session(engine) as db:
   print(json.dumps(deliver_one(db)))
 finally:
  engine.dispose()

if __name__=="__main__":
 main()

"""Production configuration preflight; no network calls or secrets logged."""
import os
from urllib.parse import urlsplit

PLACEHOLDERS=("change-me","replace-with","example","localhost","127.0.0.1")

def configuration_issues(env=None):
 e=os.environ if env is None else env
 issues=[]
 secret=e.get("AUTH_SECRET","")
 if len(secret)<32 or any(x in secret.lower() for x in PLACEHOLDERS):
  issues.append("AUTH_SECRET is missing, weak or a placeholder")
 db=e.get("DATABASE_URL","")
 try:
  u=urlsplit(db.replace("postgresql+psycopg://","postgresql://",1))
  if u.scheme!="postgresql" or not u.hostname or not u.username or not u.password:
   issues.append("DATABASE_URL requires authenticated PostgreSQL")
  if u.hostname in ("localhost","127.0.0.1") and e.get("LFM_ENV")=="production":
   issues.append("Production database must be explicitly reviewed when on loopback")
 except ValueError:
  issues.append("DATABASE_URL is invalid")
 if e.get("LFM_ENV")=="production":
  for key in ("LFM_SANDBOX_PAYMENTS_ENABLED","LFM_ITHUTE_PAY_CHECKOUT_ENABLED"):
   if e.get(key,"false").lower()=="true":
    issues.append(key+" cannot be enabled without independent release approval")
  if e.get("LFM_E2E_SEED","false").lower()=="true":
   issues.append("Synthetic E2E seeding must be disabled in production")
 return issues

def assert_safe_production_configuration(env=None):
 issues=configuration_issues(env)
 if issues:
  raise RuntimeError("Unsafe configuration: "+"; ".join(issues))

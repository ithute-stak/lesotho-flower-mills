"""Fail-closed, explicitly enabled one-shot SMTP notification delivery.

Unknown SMTP outcomes remain uncertain. They are NEVER retried automatically.
"""
import os
import smtplib
from email.message import EmailMessage
from sqlalchemy import text
from sqlalchemy.orm import Session

def configured():
 return os.getenv("LFM_FINANCE_EMAIL_DELIVERY_ENABLED")=="true"

def deliver_one(db:Session,send=None)->dict:
 if not configured():return {"enabled":False,"reason":"delivery_disabled"}
 recipient=os.getenv("LFM_FINANCE_ALERT_RECIPIENT","").strip()
 sender=os.getenv("LFM_FINANCE_ALERT_SENDER","").strip()
 host=os.getenv("LFM_FINANCE_SMTP_HOST","").strip()
 if not all((recipient,sender,host)):raise RuntimeError("Missing finance SMTP configuration")
 row=db.execute(text("""SELECT o.id,a.code,a.severity,a.details FROM finance.alert_outbox o
 JOIN finance.operational_alerts a ON a.id=o.alert_id
 WHERE o.state='pending' ORDER BY o.created_at LIMIT 1 FOR UPDATE OF o SKIP LOCKED""")).mappings().first()
 if not row:
  db.rollback()
  return {"enabled":True,"processed":0}
 db.execute(text("""UPDATE finance.alert_outbox SET state='sending',attempts=attempts+1,
 started_at=now() WHERE id=:id"""),{"id":row["id"]})
 db.commit()
 message=EmailMessage()
 message["From"]=sender;message["To"]=recipient
 message["Subject"]="LFM finance alert: "+row["code"]
 message.set_content(row["severity"].upper()+": "+row["details"])
 try:
  if send is not None:
   send(message)
  else:
   # STARTTLS only. Never send unauthenticated plaintext operational alerts.
   username=os.environ["LFM_FINANCE_SMTP_USER"]
   password=os.environ["LFM_FINANCE_SMTP_PASSWORD"]
   port=int(os.getenv("LFM_FINANCE_SMTP_PORT","587"))
   with smtplib.SMTP(host,port,timeout=15) as smtp:
    smtp.starttls()
    smtp.login(username,password)
    smtp.send_message(message)
 except Exception:
  # SMTP may have accepted an email before disconnecting; never blindly resend.
  db.execute(text("""UPDATE finance.alert_outbox SET state='uncertain',
   last_error='SMTP delivery outcome unknown' WHERE id=:id"""),{"id":row["id"]})
  db.commit()
  return {"enabled":True,"processed":1,"result":"uncertain"}
 db.execute(text("""UPDATE finance.alert_outbox SET state='sent',processed_at=now()
 WHERE id=:id"""),{"id":row["id"]})
 db.commit()
 return {"enabled":True,"processed":1,"result":"sent"}

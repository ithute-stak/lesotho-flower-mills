"""Public registration; staff-managed business approvals."""
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import db_session
from .security import current_identity, create_token, hash_password, verify_password
from .authorization import staff_identity

router = APIRouter(prefix="/api/v1", tags=["accounts"])


class Register(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=12, max_length=256)
    customer_type: str = "individual"


class Login(BaseModel):
    email: str
    password: str


@router.post("/auth/register", status_code=201)
def register(body: Register, db: Session = Depends(db_session)):
    if body.customer_type not in {"individual", "business"}:
        raise HTTPException(422, "Invalid customer type")
    identity_id, customer_id = str(uuid4()), str(uuid4())
    try:
        # Public registration never grants staff permissions or verified business privileges.
        db.execute(text("INSERT INTO crm.customers (id,customer_number,customer_type,display_name) VALUES (:id,:num,:type,:name)"),
                   {"id": customer_id, "num": "C-" + customer_id[:12].upper(), "type": body.customer_type, "name": body.name})
        db.execute(text("INSERT INTO identity.users (id,email,password_hash,role) VALUES (:id,:email,:hash,'customer')"),
                   {"id": identity_id, "email": body.email.strip().lower(), "hash": hash_password(body.password)})
        db.execute(text("INSERT INTO crm.customer_users (id,customer_id,identity_subject,membership_role) VALUES (:id,:cid,:subject,'owner')"),
                   {"id": str(uuid4()), "cid": customer_id, "subject": identity_id})
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Registration details already exist")
    return {"customer_id": customer_id, "verification_status": "pending" if body.customer_type == "business" else "not_required"}


@router.post("/auth/login")
def login(body: Login, db: Session = Depends(db_session)):
    row = db.execute(text("SELECT id,password_hash,role,active FROM identity.users WHERE email=:email"),
                     {"email": body.email.strip().lower()}).mappings().first()
    if not row or not verify_password(row["password_hash"], body.password) or not row["active"]:
        raise HTTPException(401, "Incorrect credentials")
    return {"access_token": create_token(str(row["id"]), row["role"]), "token_type": "bearer", "expires_in": 1800}


@router.get("/account/me")
def me(identity: dict = Depends(current_identity)):
    return {"user_id": identity["sub"], "role": identity["role"]}


@router.post("/businesses/{customer_id}/approve")
def approve_business(customer_id: str, identity: dict = Depends(staff_identity), db: Session = Depends(db_session)):
    result = db.execute(text("""UPDATE crm.customers SET verification_status='approved'
                              WHERE id=:cid AND customer_type='business' AND verification_status='pending'"""), {"cid": customer_id})
    if result.rowcount != 1:
        raise HTTPException(404, "Pending business not found")
    db.commit()
    return {"customer_id": customer_id, "verification_status": "approved"}

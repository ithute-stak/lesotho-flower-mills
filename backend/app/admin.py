"""Staff administration endpoints: approvals and controlled price-tier setup."""
from decimal import Decimal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .db import db_session
from .security import current_identity, require_staff

router = APIRouter(prefix="/api/v1/admin", tags=["administration"])


class TierInput(BaseModel):
    minimum_quantity: int = Field(ge=1)
    unit_price: Decimal | None = Field(default=None, ge=0)
    bundle_price: Decimal | None = Field(default=None, ge=0)


class PriceItemInput(BaseModel):
    product_id: str
    method: str
    tiers: list[TierInput] = Field(min_length=1, max_length=100)


@router.get("/businesses/pending")
def pending_businesses(identity: dict = Depends(current_identity), db: Session = Depends(db_session)):
    require_staff(identity)
    rows = db.execute(text("""SELECT id,customer_number,display_name,created_at
                              FROM crm.customers WHERE customer_type='business'
                              AND verification_status='pending' ORDER BY created_at DESC LIMIT 100""")).mappings().all()
    return [dict(row) for row in rows]


@router.get("/price-books")
def price_books(identity: dict = Depends(current_identity), db: Session = Depends(db_session)):
    require_staff(identity)
    rows = db.execute(text("SELECT id,code,name,currency,active FROM pricing.price_books ORDER BY name LIMIT 100")).mappings().all()
    return [dict(row) for row in rows]


@router.post("/price-books/{book_id}/items", status_code=201)
def create_price_item(book_id: str, body: PriceItemInput, identity: dict = Depends(current_identity), db: Session = Depends(db_session)):
    require_staff(identity)
    if body.method not in {"fixed_bundle", "volume_all_units"}:
        raise HTTPException(422, "Unsupported pricing method")
    minimums = [tier.minimum_quantity for tier in body.tiers]
    if len(minimums) != len(set(minimums)) or 1 not in minimums:
        raise HTTPException(422, "Unique pricing tiers starting at quantity 1 are required")
    if any((t.bundle_price is None or t.unit_price is not None) if body.method=="fixed_bundle" else (t.unit_price is None or t.bundle_price is not None) for t in body.tiers):
        raise HTTPException(422, "Pricing tier fields do not match method")
    item_id = str(uuid4())
    try:
        book = db.execute(text("SELECT active FROM pricing.price_books WHERE id=:id FOR UPDATE"), {"id":book_id}).mappings().first()
        if book is None:
            raise HTTPException(404, "Price book not found")
        if book["active"]:
            raise HTTPException(409, "Active price books are immutable; create a new version")
        db.execute(text("INSERT INTO pricing.price_book_items (id,price_book_id,product_id,method) VALUES (:id,:book,:product,:method)"),
                   {"id":item_id,"book":book_id,"product":body.product_id,"method":body.method})
        for tier in body.tiers:
            db.execute(text("""INSERT INTO pricing.price_tiers (id,price_book_item_id,minimum_quantity,unit_price,bundle_price)
                               VALUES (:id,:item,:quantity,:unit,:bundle)"""),
                       {"id":str(uuid4()),"item":item_id,"quantity":tier.minimum_quantity,"unit":tier.unit_price,"bundle":tier.bundle_price})
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409,"Product, price book or tier conflict")
    return {"item_id":item_id,"tiers_created":len(body.tiers),"price_book_active":False}

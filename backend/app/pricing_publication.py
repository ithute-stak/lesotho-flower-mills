"""Authorised draft review, publication and trusted price quotes."""
from decimal import Decimal
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .security import current_identity
from .db import db_session
from .pricing import PricingRequest, Tier, Method, price_order

router = APIRouter(prefix="/api/v1", tags=["published-pricing"])


def price_book_event(db: Session, book_id: UUID, actor: str, action: str):
    db.execute(text("INSERT INTO pricing.price_book_events (id, price_book_id, actor_id, action) VALUES (:id,:book,:actor,:action)"),
               {"id": str(uuid4()), "book": book_id, "actor": actor, "action": action})


@router.post("/admin/price-books/{book_id}/approve")
def approve_book(book_id: UUID, identity: dict = Depends(staff_identity), db: Session = Depends(db_session)):
    row = db.execute(text("SELECT status FROM pricing.price_books WHERE id=:id FOR UPDATE"), {"id": book_id}).mappings().first()
    if not row:
        raise HTTPException(404, "Price book not found")
    if row["status"] != "draft":
        raise HTTPException(409, "Only draft price books may be approved")
    cnt = db.execute(text("SELECT COUNT(*) FROM pricing.price_book_items WHERE price_book_id=:id"), {"id": book_id}).scalar_one()
    if cnt == 0:
        raise HTTPException(422, "A price book must contain at least one product")
    db.execute(text("UPDATE pricing.price_books SET status='approved',reviewed_by=:actor,reviewed_at=now() WHERE id=:id"),
               {"id": book_id, "actor": identity["sub"]})
    price_book_event(db,book_id,identity["sub"],"approved")
    db.commit()
    return {"id":str(book_id),"status":"approved"}


@router.post("/admin/price-books/{book_id}/publish")
def publish_book(book_id: UUID, identity: dict = Depends(staff_identity), db: Session = Depends(db_session)):
    row = db.execute(text("SELECT status,reviewed_by FROM pricing.price_books WHERE id=:id FOR UPDATE"), {"id": book_id}).mappings().first()
    if not row:
        raise HTTPException(404, "Price book not found")
    if row["status"] != "approved":
        raise HTTPException(409, "Price book must be approved first")
    if row["reviewed_by"] == identity["sub"]:
        raise HTTPException(403, "Publisher must be different from approver")
    db.execute(text("UPDATE pricing.price_books SET status='published',active=true,published_by=:actor,published_at=now() WHERE id=:id"),
               {"id":book_id,"actor":identity["sub"]})
    price_book_event(db,book_id,identity["sub"],"published")
    db.commit()
    return {"id":str(book_id),"status":"published"}


@router.get("/pricing/books/{book_id}/products/{product_id}")
def trusted_price(book_id: UUID, product_id: UUID, quantity: int, identity: dict = Depends(current_identity), db: Session = Depends(db_session)):
    if quantity < 1 or quantity > 1000000:
        raise HTTPException(422,"Invalid quantity")
    # Phase 6: default published retail book only; business customer price mapping is not yet connected.
    book=db.execute(text("SELECT status,code FROM pricing.price_books WHERE id=:id"),{"id":book_id}).mappings().first()
    if not book or book["status"]!="published":
        raise HTTPException(404,"Published price book not found")
    record=db.execute(text("SELECT id,method FROM pricing.price_book_items WHERE price_book_id=:book AND product_id=:product"),
                      {"book":book_id,"product":product_id}).mappings().first()
    if not record:
        raise HTTPException(404,"Product not priced in this book")
    rows=db.execute(text("SELECT minimum_quantity, unit_price, bundle_price FROM pricing.price_tiers WHERE price_book_item_id=:item ORDER BY minimum_quantity"),
                    {"item":record["id"]}).mappings().all()
    tiers=[Tier(minimum_quantity=r["minimum_quantity"],unit_price=r["unit_price"],bundle_price=r["bundle_price"]) for r in rows]
    result=price_order(PricingRequest(quantity=quantity, method=Method(record["method"]), tiers=tiers))
    return {"product_id":str(product_id),"book_id":str(book_id),"quantity":quantity,"total":str(result.subtotal),"currency":"LSL"}

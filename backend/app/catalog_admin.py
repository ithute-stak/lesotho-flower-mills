"""Staff-controlled product and price book management."""
from uuid import uuid4
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import db_session
from .authorization import staff_identity

router = APIRouter(prefix="/api/v1", tags=["catalog-admin"])


class ProductInput(BaseModel):
    sku: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=200)
    stock_unit: str = Field(default="bag", max_length=32)


class PriceBookInput(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=150)


@router.get("/products")
def products(db: Session = Depends(db_session)):
    rows = db.execute(text("SELECT id,sku,name,stock_unit FROM catalog.products WHERE active=true ORDER BY name LIMIT 100")).mappings().all()
    return [dict(row) for row in rows]


@router.post("/admin/products", status_code=201)
def add_product(body: ProductInput, identity: dict = Depends(staff_identity), db: Session = Depends(db_session)):
    product_id = str(uuid4())
    try:
        db.execute(text("INSERT INTO catalog.products (id,sku,name,stock_unit) VALUES (:id,:sku,:name,:unit)"),
                   {"id": product_id, "sku": body.sku, "name": body.name, "unit": body.stock_unit})
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "SKU already exists")
    return {"id": product_id, "sku": body.sku}


@router.post("/admin/price-books", status_code=201)
def add_price_book(body: PriceBookInput, identity: dict = Depends(staff_identity), db: Session = Depends(db_session)):
    book_id = str(uuid4())
    try:
        db.execute(text("INSERT INTO pricing.price_books (id,code,name,active) VALUES (:id,:code,:name,false)"),
                   {"id": book_id, "code": body.code, "name": body.name})
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Price book already exists")
    return {"id": book_id, "code": body.code, "active": False}

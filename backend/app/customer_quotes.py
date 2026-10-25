"""Customer quotation requests with server-selected, eligible published prices."""
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .db import db_session
from .security import current_identity
from .authorization import staff_identity
from .quotations import LineRequest,QuotationCreate,new_quotation

router=APIRouter(prefix="/api/v1",tags=["customer-quotations"])

class CustomerQuoteRequest(BaseModel):
    items:list[LineRequest]=Field(min_length=1,max_length=100)

class PriceAssignment(BaseModel):
    customer_id:UUID
    price_book_id:UUID

def owner_customer(db:Session,subject:str):
    rows=db.execute(text("""SELECT c.id,c.customer_type,c.verification_status
      FROM crm.customer_users cu JOIN crm.customers c ON c.id=cu.customer_id
      WHERE cu.identity_subject=:subject AND cu.membership_role='owner'"""),
      {"subject":subject}).mappings().all()
    if len(rows)!=1:
        raise HTTPException(403,"An unambiguous customer owner account is required")
    return rows[0]

def eligible_book(db:Session,customer):
    if customer["customer_type"]=="business" and customer["verification_status"]=="approved":
        rows=db.execute(text("""SELECT pb.id FROM pricing.customer_price_books cp
          JOIN pricing.price_books pb ON pb.id=cp.price_book_id
          WHERE cp.customer_id=:customer AND pb.status='published'
          AND pb.audience='business'"""),{"customer":customer["id"]}).mappings().all()
        if len(rows)==1:return rows[0]["id"]
        if len(rows)>1:raise HTTPException(409,"Multiple business price books require an explicit contract resolution")
    rows=db.execute(text("""SELECT id FROM pricing.price_books
      WHERE audience='retail' AND status='published'""")).mappings().all()
    if len(rows)!=1:
        raise HTTPException(409,"Exactly one published retail price book must be configured")
    return rows[0]["id"]

@router.post("/my/quotations",status_code=201)
def request_quote(body:CustomerQuoteRequest,identity:dict=Depends(current_identity),db:Session=Depends(db_session)):
    customer=owner_customer(db,identity["sub"])
    book=eligible_book(db,customer)
    request=QuotationCreate(customer_id=customer["id"],price_book_id=book,items=body.items)
    return new_quotation(request,db,identity["sub"])

@router.get("/my/quotations")
def my_quotes(identity:dict=Depends(current_identity),db:Session=Depends(db_session)):
    customer=owner_customer(db,identity["sub"])
    rows=db.execute(text("""SELECT id,quotation_number,status,subtotal,currency,created_at,expires_at
      FROM sales.quotations WHERE customer_id=:customer ORDER BY created_at DESC LIMIT 100"""),
      {"customer":customer["id"]}).mappings().all()
    return [dict(r) for r in rows]

@router.post("/admin/customer-price-books",status_code=201)
def assign_price_book(body:PriceAssignment,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    account=db.execute(text("SELECT customer_type,verification_status FROM crm.customers WHERE id=:id"),
      {"id":body.customer_id}).mappings().first()
    if not account or account["customer_type"]!="business" or account["verification_status"]!="approved":
        raise HTTPException(422,"Customer must be an approved business")
    book=db.execute(text("SELECT audience,status FROM pricing.price_books WHERE id=:id"),
      {"id":body.price_book_id}).mappings().first()
    if not book or book["audience"]!="business" or book["status"]!="published":
        raise HTTPException(422,"Only published business price books may be assigned")
    exists=db.execute(text("""SELECT 1 FROM pricing.customer_price_books
      WHERE customer_id=:customer AND price_book_id=:book"""),
      {"customer":body.customer_id,"book":body.price_book_id}).first()
    if exists:raise HTTPException(409,"Price book already assigned")
    db.execute(text("""INSERT INTO pricing.customer_price_books(id,customer_id,price_book_id,created_by)
      VALUES (:id,:customer,:book,:actor)"""),
      {"id":uuid4(),"customer":body.customer_id,"book":body.price_book_id,"actor":identity["sub"]})
    db.commit()
    return {"customer_id":str(body.customer_id),"price_book_id":str(body.price_book_id)}

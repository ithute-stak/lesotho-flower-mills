"""Staff-issued quotations calculated from published prices.

Customer-directed issuance awaits customer-price-book mapping and authorisation.
"""
from datetime import datetime,timedelta,timezone
from decimal import Decimal
from io import BytesIO
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from .authorization import staff_identity
from .db import db_session
from .pricing import Method,PricingRequest,Tier,price_order

router=APIRouter(prefix="/api/v1/admin/quotations",tags=["quotations"])

class LineRequest(BaseModel):
    product_id: UUID
    quantity: int=Field(ge=1,le=1000000)

class QuotationCreate(BaseModel):
    customer_id: UUID
    price_book_id: UUID
    items: list[LineRequest]=Field(min_length=1,max_length=100)
    validity_days: int=Field(default=14,ge=1,le=90)

def new_quotation(body:QuotationCreate,db:Session,actor:str):
    if len({x.product_id for x in body.items})!=len(body.items):
        raise HTTPException(422,"Duplicate product lines must be combined")
    book=db.execute(text("SELECT status,currency FROM pricing.price_books WHERE id=:id"),
        {"id":body.price_book_id}).mappings().first()
    if not book or book["status"]!="published":
        raise HTTPException(422,"A published price book is required")
    if book["currency"]!="LSL":
        raise HTTPException(422,"Unsupported currency")
    customer=db.execute(text("SELECT customer_type,verification_status FROM crm.customers WHERE id=:id"),
        {"id":body.customer_id}).mappings().first()
    if not customer:
        raise HTTPException(404,"Customer not found")
    if customer["customer_type"]=="business" and customer["verification_status"]!="approved":
        raise HTTPException(403,"Business requires verification before receiving a quotation")
    lines=[]
    subtotal=Decimal("0.00")
    for entry in body.items:
        row=db.execute(text("""SELECT p.sku,p.name,i.id AS item_id,i.method
          FROM pricing.price_book_items i
          JOIN catalog.products p ON p.id=i.product_id
          WHERE i.price_book_id=:book AND i.product_id=:product AND p.active=true"""),
          {"book":body.price_book_id,"product":entry.product_id}).mappings().first()
        if not row:
            raise HTTPException(422,"Product is unavailable or not in published price book")
        stored=db.execute(text("""SELECT minimum_quantity,unit_price,bundle_price
          FROM pricing.price_tiers WHERE price_book_item_id=:item ORDER BY minimum_quantity"""),
          {"item":row["item_id"]}).mappings().all()
        try:
            calculated=price_order(PricingRequest(quantity=entry.quantity,
              method=Method(row["method"]),tiers=[Tier(**dict(t)) for t in stored]))
        except (ValueError,TypeError):
            raise HTTPException(422,"Invalid stored price rules")
        subtotal+=calculated.subtotal
        lines.append((entry,row,calculated.subtotal))
    quote_id=uuid4()
    reference="LFM-QT-"+datetime.now(timezone.utc).strftime("%Y%m%d")+"-"+str(quote_id)[:8].upper()
    expiry=datetime.now(timezone.utc)+timedelta(days=body.validity_days)
    db.execute(text("""INSERT INTO sales.quotations
      (id,quotation_number,customer_id,price_book_id,status,subtotal,created_by,expires_at)
      VALUES (:id,:number,:customer,:book,'draft',:total,:actor,:expiry)"""),
      {"id":quote_id,"number":reference,"customer":body.customer_id,
       "book":body.price_book_id,"total":subtotal,"actor":actor,"expiry":expiry})
    for entry,row,total in lines:
        db.execute(text("""INSERT INTO sales.quotation_items
          (id,quotation_id,product_id,sku_snapshot,product_name_snapshot,quantity,pricing_method_snapshot,line_total)
          VALUES (:id,:quote,:product,:sku,:name,:quantity,:method,:total)"""),
          {"id":uuid4(),"quote":quote_id,"product":entry.product_id,"sku":row["sku"],
           "name":row["name"],"quantity":entry.quantity,"method":row["method"],"total":total})
    db.commit()
    return {"id":str(quote_id),"quotation_number":reference,"status":"draft","subtotal":str(subtotal),"currency":"LSL","expires_at":expiry.isoformat()}

@router.post("",status_code=201)
def create_quote(body:QuotationCreate,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    return new_quotation(body,db,identity["sub"])

@router.get("/{quotation_id}")
def get_quote(quotation_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    quotation=db.execute(text("SELECT * FROM sales.quotations WHERE id=:id"),{"id":quotation_id}).mappings().first()
    if not quotation:raise HTTPException(404,"Quotation not found")
    rows=db.execute(text("SELECT sku_snapshot,product_name_snapshot,quantity,line_total FROM sales.quotation_items WHERE quotation_id=:id ORDER BY product_name_snapshot"),{"id":quotation_id}).mappings().all()
    return {"quotation":dict(quotation),"items":[dict(r) for r in rows]}

@router.get("/{quotation_id}/pdf")
def quotation_pdf(quotation_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    record=get_quote(quotation_id,identity,db)
    q=record["quotation"]
    output=BytesIO()
    document=SimpleDocTemplate(output,pagesize=A4,topMargin=40,bottomMargin=40)
    styles=getSampleStyleSheet()
    story=[Paragraph("LESOTHO FLOUR MILLS",styles["Title"]),
           Paragraph("DRAFT QUOTATION — NOT A TAX INVOICE",styles["Heading2"]),
           Paragraph("Reference: "+q["quotation_number"],styles["Normal"]),
           Paragraph("Customer reference: "+str(q["customer_id"]),styles["Normal"]),
           Paragraph("Valid until: "+q["expires_at"].strftime("%Y-%m-%d"),styles["Normal"]),
           Spacer(1,18)]
    data=[["SKU","Product","Qty","Amount (LSL)"]]
    for item in record["items"]:
        data.append([item["sku_snapshot"],item["product_name_snapshot"],str(item["quantity"]),f'{item["line_total"]:,.2f}'])
    data.append(["","","SUBTOTAL",f'{q["subtotal"]:,.2f}'])
    table=Table(data,colWidths=[95,225,50,105],repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#174d36")),
      ("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.3,colors.grey),
      ("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),8)]))
    story.extend([table,Spacer(1,15),Paragraph("Delivery, stock allocation and any applicable taxes remain subject to final confirmation. No order has been placed.",styles["Normal"])])
    document.build(story);output.seek(0)
    return StreamingResponse(output,media_type="application/pdf",
      headers={"Content-Disposition":f'attachment; filename="{q["quotation_number"]}.pdf"'})

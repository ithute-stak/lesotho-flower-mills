"""Provider-neutral payment initiation (sandbox only).

No live providers are configured. Never treat client-returned payment state as
settlement evidence. The sandbox intentionally cannot confirm orders.
"""
import os
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .finance_permissions import finance_read,finance_review
from .db import db_session

router=APIRouter(prefix="/api/v1/admin/payment-gateway",tags=["payment-gateway"])

@dataclass(frozen=True)
class PaymentIntent:
    provider_reference:str
    state:str
    redirect_url:str|None=None

class GatewayProvider:
    def initiate(self,amount:Decimal,currency:str,order_id:UUID)->PaymentIntent:
        raise NotImplementedError

class SandboxProvider(GatewayProvider):
    def initiate(self,amount:Decimal,currency:str,order_id:UUID)->PaymentIntent:
        return PaymentIntent(provider_reference="sandbox-"+str(uuid4()),state="pending")

PROVIDERS:dict[str,GatewayProvider]={"sandbox":SandboxProvider()}

class InitiateRequest(BaseModel):
    order_id:UUID
    provider:str=Field(min_length=2,max_length=60)

@router.post("/initiate",status_code=201)
def initiate(body:InitiateRequest,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
    if os.getenv("LFM_SANDBOX_PAYMENTS_ENABLED")!="true":
        raise HTTPException(503,"Sandbox payment initiation disabled")
    provider=PROVIDERS.get(body.provider)
    if provider is None:
        raise HTTPException(422,"Payment provider is not integrated")
    order=db.execute(text("SELECT id,status,subtotal FROM sales.sales_orders WHERE id=:id FOR UPDATE"),
        {"id":body.order_id}).mappings().first()
    if not order:
        raise HTTPException(404,"Order not found")
    if order["status"]!="pending_payment":
        raise HTTPException(409,"Order is not awaiting payment")
    intent=provider.initiate(Decimal(order["subtotal"]),"LSL",body.order_id)
    db.execute(text("""INSERT INTO finance.payment_transactions
        (id,sales_order_id,provider,provider_reference,amount,currency,verification_status)
        VALUES (:id,:order,:provider,:reference,:amount,'LSL','pending')"""),
        {"id":uuid4(),"order":body.order_id,"provider":body.provider,
         "reference":intent.provider_reference,"amount":order["subtotal"]})
    db.commit()
    return {"provider":body.provider,"provider_reference":intent.provider_reference,
        "status":"pending","amount":str(order["subtotal"]),"currency":"LSL",
        "payment_url":intent.redirect_url,"can_confirm_order":False}

@router.get("/providers")
def providers(identity:dict=Depends(finance_read)):
    return {"available_sandbox":["sandbox"] if os.getenv("LFM_SANDBOX_PAYMENTS_ENABLED")=="true" else [],
            "live_integrations":[],"payment_confirmation_enabled":False}

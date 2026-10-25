"""Phase 2 public catalogue and pricing contract.

Catalogue data is read-only; official LFM prices must be authorised before publication.
Customer registration is intentionally not exposed until identity verification is built.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from .pricing import PricingRequest, PricingResult, price_order

router = APIRouter(prefix="/api/v1", tags=["commerce"])


class Category(BaseModel):
    slug: str
    label: str


@router.get("/categories", response_model=list[Category])
def categories():
    return [
        Category(slug="feed", label="Animal Feed"),
        Category(slug="maize", label="Maize Milling"),
        Category(slug="flour", label="Flour Milling"),
        Category(slug="sugar", label="Sugar"),
    ]


@router.post("/pricing/preview", response_model=PricingResult)
def preview_pricing(request: PricingRequest):
    """Quotation preview for an explicitly supplied untrusted price schedule.
    Does not create a quotation, verify stock or bind an official product price.
    """
    return price_order(request)

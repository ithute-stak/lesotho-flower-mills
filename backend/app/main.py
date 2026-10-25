from fastapi import FastAPI
from .commerce import router as commerce_router
from .accounts import router as accounts_router
from .catalog_admin import router as catalog_router
from .admin import router as admin_router
from .pricing_publication import router as pricing_publication_router
from .quotations import router as quotations_router
from .customer_quotes import router as customer_quote_router
from .stock import router as stock_router
from .orders import router as orders_router
from .warehouse_ops import router as warehouse_router
from .fulfilment import router as fulfilment_router
from .payment_authorisation import router as payment_router
from .payment_gateway import router as gateway_router
from .delivery_ops import router as delivery_router
from .driver_portal import router as driver_portal_router

app = FastAPI(title="Lesotho Flour Mills API", description="Hybrid B2C/B2B commerce and distribution platform", version="0.4.0")
app.include_router(commerce_router)
app.include_router(accounts_router)
app.include_router(catalog_router)
app.include_router(admin_router)
app.include_router(pricing_publication_router)
app.include_router(quotations_router)
app.include_router(customer_quote_router)
app.include_router(stock_router)
app.include_router(orders_router)
app.include_router(warehouse_router)
app.include_router(fulfilment_router)
app.include_router(payment_router)
app.include_router(gateway_router)
app.include_router(delivery_router)
app.include_router(driver_portal_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1", tags=["system"])
def api_root() -> dict[str, str]:
    return {"service": "lfm-commerce", "version": "v1"}

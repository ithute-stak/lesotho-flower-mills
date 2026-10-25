from fastapi import FastAPI
from .commerce import router as commerce_router
from .accounts import router as accounts_router
from .catalog_admin import router as catalog_router
from .admin import router as admin_router
from .pricing_publication import router as pricing_publication_router
from .quotations import router as quotations_router

app = FastAPI(title="Lesotho Flour Mills API", description="Hybrid B2C/B2B commerce and distribution platform", version="0.4.0")
app.include_router(commerce_router)
app.include_router(accounts_router)
app.include_router(catalog_router)
app.include_router(admin_router)
app.include_router(pricing_publication_router)
app.include_router(quotations_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1", tags=["system"])
def api_root() -> dict[str, str]:
    return {"service": "lfm-commerce", "version": "v1"}

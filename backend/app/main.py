from fastapi import FastAPI

app = FastAPI(
    title="Lesotho Flour Mills API",
    description="Hybrid B2C/B2B commerce and distribution platform",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1", tags=["system"])
def api_root() -> dict[str, str]:
    return {"service": "lfm-commerce", "version": "v1"}

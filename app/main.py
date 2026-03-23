"""FastAPI application creation, middleware, and startup configuration."""
from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.routers.contacts import router as contacts_router
from app.routers.companies import router as companies_router
from app.routers.deals import router as deals_router
from app.routers.activities import router as activities_router
from app.routers.tags import router as tags_router

app = FastAPI(title="Mini CRM", version="0.1.0")

app.include_router(auth_router)
app.include_router(contacts_router)
app.include_router(companies_router)
app.include_router(deals_router)
app.include_router(activities_router)
app.include_router(tags_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

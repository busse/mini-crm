"""FastAPI application creation, middleware, and startup configuration."""
from fastapi import FastAPI

from app.auth.router import router as auth_router

app = FastAPI(title="Mini CRM", version="0.1.0")

app.include_router(auth_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

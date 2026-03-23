"""FastAPI application creation, middleware, and startup configuration."""
from fastapi import FastAPI

app = FastAPI(title="Mini CRM", version="0.1.0")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

"""
API v1 router aggregation.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, gpt

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    tags=["Health"]
)

api_router.include_router(
    gpt.router,
    tags=["GPT"]
)
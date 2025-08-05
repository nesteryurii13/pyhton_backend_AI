"""
Health check endpoints.
"""
import os
from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from app.models.schemas import HealthResponse
from app.services.gpt_service import GPTService
from app.api.deps import get_current_gpt_service
from app.core.logging import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API and its dependencies"
)
async def health_check(
    gpt_service: GPTService = Depends(get_current_gpt_service)
) -> HealthResponse:
    """
    Perform a comprehensive health check of the API.
    
    Returns:
        Health status of the API and its dependencies
    """
    logger.info("Health check requested")
    
    # Check GPT service health
    gpt_health = await gpt_service.health_check()
    
    # Determine overall health status
    overall_status = "healthy" if gpt_health["status"] == "healthy" else "degraded"
    
    if overall_status == "degraded":
        logger.warning(f"Health check shows degraded status: {gpt_health}")
    
    # Get settings from environment variables
    project_name = os.getenv("PROJECT_NAME", "GPT Query API")
    version = os.getenv("VERSION", "1.0.0")
    
    return HealthResponse(
        status=overall_status,
        service=project_name,
        version=version
    )
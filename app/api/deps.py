"""
Dependencies for API endpoints.
"""
from app.services.gpt_service import get_gpt_service, GPTService


async def get_current_gpt_service() -> GPTService:
    """Get the current GPT service instance."""
    return await get_gpt_service()
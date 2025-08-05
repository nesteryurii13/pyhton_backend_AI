"""
Pytest configuration and fixtures.
"""
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from GPT."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "total_tokens": 50
        }
    }
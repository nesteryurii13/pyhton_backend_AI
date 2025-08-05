"""
Tests for health check endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint."""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "service" in data
    assert "version" in data
    assert "docs_url" in data
    assert "health_url" in data
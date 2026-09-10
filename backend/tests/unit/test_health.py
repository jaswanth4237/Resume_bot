import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "data" in json_data
    assert "services" in json_data["data"]
    assert "requestId" in json_data
    assert json_data["data"]["services"]["database"] in ["connected", "disconnected"]

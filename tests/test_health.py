from httpx import AsyncClient


class TestHealthEndpoint:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

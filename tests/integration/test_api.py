"""Integration tests for the API server."""

import pytest
from httpx import AsyncClient, ASGITransport
from api.server import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "nexus-ai"


class TestWorkflowTemplates:
    @pytest.mark.asyncio
    async def test_get_templates(self, client):
        response = await client.get("/api/v1/workflows/templates/all")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert data["total"] > 0
        assert "full_business_setup" in data["templates"]


class TestAgentEndpoints:
    @pytest.mark.asyncio
    async def test_list_agents(self, client):
        response = await client.get("/api/v1/agents/")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data

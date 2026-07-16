from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from research_agent.main import app


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_research_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/research",
            json={
                "question": "What is the impact of AI?",
                "max_results_per_source": 2,
                "include_sources": ["news", "web"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("completed", "partial", "failed")
        if data["status"] != "failed":
            assert "report_markdown" in data


@pytest.mark.asyncio
async def test_research_endpoint_empty_question() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/research",
            json={"question": "", "include_sources": ["news"]},
        )
        data = resp.json()
        assert data["status"] == "failed"


@pytest.mark.asyncio
async def test_metrics_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/metrics")
        assert resp.status_code == 200

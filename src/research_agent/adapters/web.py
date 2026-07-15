from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup

from research_agent.adapters.base import BaseSearchAdapter, RawDocument, RawSearchResult
from research_agent.config import settings
from research_agent.planning.query_planner import SearchPlan
from research_agent.security.url_safety import (
    REQUEST_TIMEOUT,
    assert_safe_url,
)
from research_agent.utils.urls import canonicalise


class WebSearchAdapter(BaseSearchAdapter):
    source_type = "web"

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            max_redirects=5,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/0.1; +https://research-agent.dev)",
            },
        )

    async def search_for_query(self, query: str) -> list[RawSearchResult]:
        # Uses Tavily if key is available, otherwise returns empty
        if not settings.tavily_api_key:
            return []
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": settings.tavily_api_key,
                        "query": query,
                        "search_depth": "advanced",
                        "max_results": settings.max_results_per_source,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return [
                    RawSearchResult(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        snippet=r.get("content", ""),
                        source_type="web",
                        publisher=r.get("domain", ""),
                        score=r.get("score", 0.0),
                    )
                    for r in data.get("results", [])
                ]
        except httpx.HTTPError:
            return []

    async def search(self, plan: SearchPlan) -> list[RawSearchResult]:
        return await self.search_all_queries(plan)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        assert_safe_url(result.url)
        try:
            resp = await self.client.get(result.url)
            resp.raise_for_status()
            html = resp.text
            text = self._extract_text(html)
            return RawDocument(
                url=result.url,
                title=result.title,
                source_type="web",
                html=html,
                text=text,
                effective_url=canonicalise(str(resp.url)),
                status_code=resp.status_code,
            )
        except httpx.HTTPError as e:
            return RawDocument(
                url=result.url,
                title=result.title,
                source_type="web",
                text=f"Failed to fetch: {e}",
                status_code=getattr(e.response, "status_code", 0),
            )

    def _extract_text(self, html: str) -> str:
        try:
            import trafilatura
            text = trafilatura.extract(html)
            if text:
                return text
        except Exception:
            pass
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[: settings.max_response_size_bytes]

    async def close(self) -> None:
        await self.client.aclose()

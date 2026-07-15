from __future__ import annotations

import httpx

from research_agent.adapters.base import BaseSearchAdapter, RawDocument, RawSearchResult
from research_agent.config import settings
from research_agent.planning.query_planner import SearchPlan


class NewsSearchAdapter(BaseSearchAdapter):
    source_type = "news"

    async def search_for_query(self, query: str) -> list[RawSearchResult]:
        if not settings.bing_news_api_key:
            return []
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    "https://api.bing.microsoft.com/v7.0/news/search",
                    headers={"Ocp-Apim-Subscription-Key": settings.bing_news_api_key},
                    params={
                        "q": query,
                        "count": settings.max_results_per_source,
                        "freshness": "Week",
                        "mkt": "en-US",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                results = []
                for item in data.get("value", []):
                    results.append(
                        RawSearchResult(
                            title=item.get("name", ""),
                            url=item.get("url", ""),
                            snippet=item.get("description", ""),
                            source_type="news",
                            publisher=item.get("provider", [{}])[0].get("name", "")
                            if item.get("provider") else "",
                            published_at=item.get("datePublished", ""),
                            score=0.8,
                        )
                    )
                return results
        except httpx.HTTPError:
            return []

    async def search(self, plan: SearchPlan) -> list[RawSearchResult]:
        return await self.search_all_queries(plan)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        from research_agent.adapters.web import WebSearchAdapter
        web = WebSearchAdapter()
        return await web.fetch(result)

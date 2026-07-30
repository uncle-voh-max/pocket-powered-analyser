from __future__ import annotations

import httpx

from research_agent.adapters.base import BaseSearchAdapter, RawDocument, RawSearchResult
from research_agent.planning.query_planner import SearchPlan


class SocialSearchAdapter(BaseSearchAdapter):
    """Generic social media adapter interface.

    Currently returns mock data. To add a real backend (X/Twitter, Mastodon,
    Bluesky, Hacker News, etc.), subclass this and override search_for_query.
    """

    source_type = "social"

    async def search_for_query(
        self,
        query: str,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        # Hacker News Algolia search — free, no auth
        # extend this to other social media platforms as needed
        limit = max_results if max_results is not None else 5
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={"query": query, "hitsPerPage": limit, "tags": "story"},
                )
                resp.raise_for_status()
                data = resp.json()
                results = []
                for hit in data.get("hits", []):
                    results.append(
                        RawSearchResult(
                            title=hit.get("title", ""),
                            url=hit.get("url")
                            or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                            snippet=hit.get("story_text", "")[:300] or "",
                            source_type="social",
                            publisher="Hacker News",
                            author=hit.get("author", ""),
                            score=min((hit.get("points", 0) or 0) / 100.0, 1.0),
                        )
                    )
                return results
        except httpx.HTTPError:
            return []

    async def search(
        self,
        plan: SearchPlan,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return await self.search_all_queries(plan, max_results=max_results)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        import re
        import httpx as _httpx
        try:
            async with _httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(
                    result.url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/0.1)",
                    },
                )
                resp.raise_for_status()
                html = resp.text
                text = re.sub(r"<[^>]+>", " ", html)
                text = re.sub(r"\s+", " ", text)[:3000]
                return RawDocument(
                    url=result.url,
                    title=result.title,
                    source_type="social",
                    text=text,
                    effective_url=str(resp.url),
                    status_code=resp.status_code,
                )
        except _httpx.HTTPError as e:
            return RawDocument(
                url=result.url,
                title=result.title,
                source_type="social",
                text=f"Failed to fetch: {e}",
                status_code=0,
            )

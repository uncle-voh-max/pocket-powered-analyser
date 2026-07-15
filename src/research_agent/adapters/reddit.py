from __future__ import annotations

import httpx

from research_agent.adapters.base import BaseSearchAdapter, RawDocument, RawSearchResult
from research_agent.config import settings
from research_agent.planning.query_planner import SearchPlan
from research_agent.utils.dates import parse_iso_date


class RedditSearchAdapter(BaseSearchAdapter):
    source_type = "reddit"

    async def _get_auth_token(self, client: httpx.AsyncClient) -> str | None:
        if not settings.has_reddit_creds:
            return None
        try:
            resp = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=(settings.reddit_client_id, settings.reddit_client_secret),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": settings.reddit_user_agent},
            )
            resp.raise_for_status()
            return resp.json().get("access_token")
        except httpx.HTTPError:
            return None

    async def search_for_query(self, query: str) -> list[RawSearchResult]:
        if not settings.has_reddit_creds:
            return []
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                token = await self._get_auth_token(client)
                if not token:
                    return []
                headers = {
                    "Authorization": f"Bearer {token}",
                    "User-Agent": settings.reddit_user_agent,
                }
                resp = await client.get(
                    "https://oauth.reddit.com/search",
                    headers=headers,
                    params={"q": query, "limit": 10, "sort": "relevance"},
                )
                resp.raise_for_status()
                data = resp.json()
                results = []
                for child in data.get("data", {}).get("children", []):
                    d = child.get("data", {})
                    results.append(
                        RawSearchResult(
                            title=d.get("title", ""),
                            url=f"https://reddit.com{d.get('permalink', '')}",
                            snippet=d.get("selftext", "")[:300] or d.get("title", ""),
                            source_type="reddit",
                            publisher=f"r/{d.get('subreddit', 'unknown')}",
                            author=d.get("author", ""),
                            published_at=parse_iso_date(
                                str(d.get("created_utc", ""))
                            ),
                            score=min((d.get("score", 0) or 0) / 100.0, 1.0),
                        )
                    )
                return results
        except httpx.HTTPError:
            return []

    async def search(self, plan: SearchPlan) -> list[RawSearchResult]:
        return await self.search_all_queries(plan)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        import re
        import httpx as _httpx
        try:
            async with _httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(
                    result.url,
                    headers={"User-Agent": settings.reddit_user_agent},
                )
                resp.raise_for_status()
                html = resp.text
                text = re.sub(r"<[^>]+>", " ", html)
                text = re.sub(r"\s+", " ", text)[:5000]
                return RawDocument(
                    url=result.url,
                    title=result.title,
                    source_type="reddit",
                    text=text,
                    effective_url=str(resp.url),
                    status_code=resp.status_code,
                )
        except _httpx.HTTPError as e:
            return RawDocument(
                url=result.url,
                title=result.title,
                source_type="reddit",
                text=f"Failed to fetch: {e}",
                status_code=0,
            )

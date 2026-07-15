from __future__ import annotations

import httpx

from research_agent.adapters.base import BaseSearchAdapter, RawDocument, RawSearchResult
from research_agent.planning.query_planner import SearchPlan


class WikipediaSearchAdapter(BaseSearchAdapter):
    source_type = "wikipedia"
    BASE_URL = "https://en.wikipedia.org/w/api.php"

    async def search_for_query(self, query: str) -> list[RawSearchResult]:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    self.BASE_URL,
                    params={
                        "action": "query",
                        "list": "search",
                        "srsearch": query,
                        "format": "json",
                        "srlimit": 5,
                        "srprop": "snippet|titlesnippet",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                results = []
                for page in data.get("query", {}).get("search", []):
                    page_title = page.get("title", "")
                    results.append(
                        RawSearchResult(
                            title=f"{page_title} - Wikipedia",
                            url=f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                            snippet=page.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                            source_type="wikipedia",
                            publisher="Wikipedia",
                            score=page.get("score", 0) / 1000.0 if page.get("score") else 0.5,
                        )
                    )
                return results
        except httpx.HTTPError:
            return []

    async def search(self, plan: SearchPlan) -> list[RawSearchResult]:
        return await self.search_all_queries(plan)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        page_title = result.url.split("/wiki/")[-1].replace("_", " ") if "/wiki/" in result.url else result.title
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    self.BASE_URL,
                    params={
                        "action": "query",
                        "prop": "extracts|info",
                        "exintro": False,
                        "explaintext": True,
                        "titles": page_title,
                        "format": "json",
                        "inprop": "url",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    if page_id == "-1":
                        text = f"Wikipedia page not found for: {page_title}"
                    else:
                        text = page_data.get("extract", "No extract available.")
                        actual_url = page_data.get("fullurl", result.url)
                        return RawDocument(
                            url=result.url,
                            title=page_data.get("title", result.title),
                            source_type="wikipedia",
                            text=text[:10000],
                            effective_url=actual_url,
                            status_code=200,
                        )
                return RawDocument(
                    url=result.url,
                    title=result.title,
                    source_type="wikipedia",
                    text="No content retrieved from Wikipedia.",
                    status_code=404,
                )
        except httpx.HTTPError as e:
            return RawDocument(
                url=result.url,
                title=result.title,
                source_type="wikipedia",
                text=f"Failed to fetch Wikipedia page: {e}",
                status_code=0,
            )

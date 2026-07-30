from __future__ import annotations

from datetime import datetime, timedelta, timezone

from research_agent.adapters.base import BaseSearchAdapter, RawDocument, RawSearchResult
from research_agent.planning.query_planner import SearchPlan


class MockNewsAdapter(BaseSearchAdapter):
    source_type = "news"

    async def search_for_query(
        self,
        query: str,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return [
            RawSearchResult(
                title=f"News: Latest developments related to '{query}'",
                url=f"https://news.example.com/article?q={query.replace(' ', '+')}",
                snippet=f"An in-depth article discussing recent findings about {query}. "
                f"Includes expert analysis and commentary.",
                source_type="news",
                publisher="Example News",
                author="Jane Doe",
                published_at=datetime.now(timezone.utc) - timedelta(hours=2),
                score=0.92,
            ),
            RawSearchResult(
                title=f"Breaking: New insights on {query}",
                url=f"https://news.example.com/breaking?q={query.replace(' ', '+')}",
                snippet=f"Breaking news coverage of developments in {query}. "
                f"Multiple sources confirm.",
                source_type="news",
                publisher="Example News",
                published_at=datetime.now(timezone.utc) - timedelta(hours=6),
                score=0.85,
            ),
        ]

    async def search(
        self,
        plan: SearchPlan,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return await self.search_all_queries(plan, max_results=max_results)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        return RawDocument(
            url=result.url,
            title=result.title,
            source_type="news",
            text=f"This is the full article text for: {result.title}\n\n"
            f"{result.snippet}\n\n"
            f"Additional paragraphs providing more detail and context. "
            f"Experts weighed in on the significance of these developments.",
            effective_url=result.url,
            status_code=200,
        )


class MockWebAdapter(BaseSearchAdapter):
    source_type = "web"

    async def search_for_query(
        self,
        query: str,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return [
            RawSearchResult(
                title=f"Complete Guide to {query}",
                url=f"https://docs.example.com/guide/{query.replace(' ', '-').lower()}",
                snippet=f"A comprehensive guide covering all aspects of {query}. "
                f"Covers fundamentals, advanced topics, and best practices.",
                source_type="web",
                publisher="Example Docs",
                author="Tech Writer",
                score=0.95,
            ),
            RawSearchResult(
                title=f"Analysis Report: {query} Trends",
                url=f"https://research.example.com/papers/{query.replace(' ', '-').lower()}",
                snippet=f"Research paper examining current trends and future directions in {query}. "
                f"Peer-reviewed. Published quarterly.",
                source_type="web",
                publisher="Research Institute",
                author="Dr. Smith",
                published_at=datetime.now(timezone.utc) - timedelta(days=30),
                score=0.88,
            ),
        ]

    async def search(
        self,
        plan: SearchPlan,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return await self.search_all_queries(plan, max_results=max_results)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        return RawDocument(
            url=result.url,
            title=result.title,
            source_type="web",
            text=f"Full article: {result.title}\n\n"
            f"{result.snippet}\n\n"
            f"Detailed sections with technical analysis, data tables, and references.",
            effective_url=result.url,
            status_code=200,
        )


class MockRedditAdapter(BaseSearchAdapter):
    source_type = "reddit"

    async def search_for_query(
        self,
        query: str,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return [
            RawSearchResult(
                title=f"r/technology: What does everyone think about {query}?",
                url=f"https://reddit.com/r/technology/comments/1abc/",
                snippet=f"User discussion about {query}. Top comments highlight "
                f"concerns about privacy and adoption rates.",
                source_type="reddit",
                publisher="reddit.com",
                published_at=datetime.now(timezone.utc) - timedelta(days=3),
                score=0.65,
            ),
        ]

    async def search(
        self,
        plan: SearchPlan,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return await self.search_all_queries(plan, max_results=max_results)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        return RawDocument(
            url=result.url,
            title=result.title,
            source_type="reddit",
            text=f"Post: {result.title}\n\n{result.snippet}\n\n"
            f"--- Top Comments ---\n"
            f"User1: This is a really interesting point. I think the implications are huge.\n"
            f"User2: Can someone explain how this actually works? ELI5?\n"
            f"User3: I work in this field and here are my thoughts... [detailed analysis]",
            effective_url=result.url,
            status_code=200,
        )


class MockSocialAdapter(BaseSearchAdapter):
    source_type = "social"

    async def search_for_query(
        self,
        query: str,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return [
            RawSearchResult(
                title=f"Post about {query}",
                url=f"https://social.example.com/post/12345",
                snippet=f"Viral thread discussing {query}. "
                f"Over 10k likes and 2k reposts.",
                source_type="social",
                publisher="social.example.com",
                published_at=datetime.now(timezone.utc) - timedelta(hours=12),
                score=0.5,
            ),
        ]

    async def search(
        self,
        plan: SearchPlan,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return await self.search_all_queries(plan, max_results=max_results)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        return RawDocument(
            url=result.url,
            title=result.title,
            source_type="social",
            text=f"Social post: {result.title}\n\n{result.snippet}",
            effective_url=result.url,
            status_code=200,
        )


class MockWikipediaAdapter(BaseSearchAdapter):
    source_type = "wikipedia"

    async def search_for_query(
        self,
        query: str,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return [
            RawSearchResult(
                title=f"{query} - Wikipedia",
                url=f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                snippet=f"This article provides an overview of {query}, "
                f"including its history, key concepts, and significance.",
                source_type="wikipedia",
                publisher="Wikipedia",
                score=0.7,
            ),
        ]

    async def search(
        self,
        plan: SearchPlan,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        return await self.search_all_queries(plan, max_results=max_results)

    async def fetch(self, result: RawSearchResult) -> RawDocument:
        return RawDocument(
            url=result.url,
            title=result.title,
            source_type="wikipedia",
            text=f"Wikipedia article: {result.title}\n\n"
            f"{result.snippet}\n\n"
            f"== History ==\nThe concept dates back to early research.\n\n"
            f"== Key Concepts ==\nThe main ideas include...\n\n"
            f"== Significance ==\nThis topic is important because...\n\n"
            f"== References ==\n1. Reference 1\n2. Reference 2",
            effective_url=result.url,
            status_code=200,
        )


def get_mock_adapter(source_type: str) -> BaseSearchAdapter:
    adapters = {
        "news": MockNewsAdapter(),
        "web": MockWebAdapter(),
        "reddit": MockRedditAdapter(),
        "social": MockSocialAdapter(),
        "wikipedia": MockWikipediaAdapter(),
    }
    return adapters[source_type]

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from research_agent.planning.query_planner import SearchPlan
from research_agent.utils.dates import utcnow


@dataclass
class RawSearchResult:
    title: str
    url: str
    snippet: str = ""
    source_type: str = "unknown"
    publisher: str = ""
    author: str = ""
    published_at: datetime | None = None
    retrieved_at: datetime = field(default_factory=utcnow)
    score: float = 0.0


@dataclass
class RawDocument:
    url: str = ""
    title: str = ""
    source_type: str = "unknown"
    html: str = ""
    text: str = ""
    effective_url: str = ""
    status_code: int = 0
    retrieved_at: datetime = field(default_factory=utcnow)


class BaseSearchAdapter(ABC):
    source_type: str = "unknown"

    @abstractmethod
    async def search(
        self,
        plan: SearchPlan,
        max_results: int | None = None,
    ) -> list[RawSearchResult]: ...

    @abstractmethod
    async def fetch(self, result: RawSearchResult) -> RawDocument: ...

    async def search_all_queries(
        self,
        plan: SearchPlan,
        max_results: int | None = None,
    ) -> list[RawSearchResult]:
        all_results: list[RawSearchResult] = []
        queries = self._queries_for_plan(plan)
        for query in queries:
            try:
                results = await self.search_for_query(query, max_results=max_results)
                all_results.extend(results)
            except Exception:
                continue
        return all_results

    @abstractmethod
    async def search_for_query(
        self,
        query: str,
        max_results: int | None = None,
    ) -> list[RawSearchResult]: ...

    def _queries_for_plan(self, plan: SearchPlan) -> list[str]:
        return getattr(plan, self.source_type, [])

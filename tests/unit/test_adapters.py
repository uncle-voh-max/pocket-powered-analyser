from __future__ import annotations

import pytest

from research_agent.adapters.base import BaseSearchAdapter, RawDocument, RawSearchResult
from research_agent.adapters.mock import (
    MockNewsAdapter,
    MockWebAdapter,
    MockRedditAdapter,
    MockSocialAdapter,
    MockWikipediaAdapter,
    get_mock_adapter,
)
from research_agent.planning.query_planner import SearchPlan


class TestMockAdapters:
    @pytest.fixture
    def plan(self) -> SearchPlan:
        return SearchPlan(
            news=["test query"],
            web=["test query"],
            social=["test query"],
            reddit=["test query"],
            wikipedia=["test query"],
        )

    @pytest.mark.parametrize(
        "adapter_cls,source_type",
        [
            (MockNewsAdapter, "news"),
            (MockWebAdapter, "web"),
            (MockRedditAdapter, "reddit"),
            (MockSocialAdapter, "social"),
            (MockWikipediaAdapter, "wikipedia"),
        ],
    )
    async def test_adapter_interface(
        self,
        adapter_cls: type[BaseSearchAdapter],
        source_type: str,
        plan: SearchPlan,
    ) -> None:
        adapter = adapter_cls()
        assert adapter.source_type == source_type

        results = await adapter.search(plan)
        assert isinstance(results, list)
        assert len(results) > 0

        result = results[0]
        assert isinstance(result, RawSearchResult)
        assert result.title
        assert result.url
        assert result.source_type == source_type

        doc = await adapter.fetch(result)
        assert isinstance(doc, RawDocument)
        assert doc.text
        assert doc.url

    async def test_get_mock_adapter(self) -> None:
        adapter = get_mock_adapter("news")
        assert isinstance(adapter, MockNewsAdapter)

    async def test_mock_adapter_empty_plan(self) -> None:
        adapter = MockNewsAdapter()
        plan = SearchPlan()
        results = await adapter.search(plan)
        assert results == []

from __future__ import annotations

import pytest

from research_agent.graph.state import ResearchState
from research_agent.graph.workflow import build_graph

CONFIG = {"configurable": {"thread_id": "test"}}

@pytest.mark.asyncio
async def test_graph_execution_with_mock_adapters() -> None:
    """Test the full graph runs to completion with mock adapters."""
    graph = build_graph(checkpointer=True)
    initial = ResearchState(
        question="What are the latest developments in AI safety?",
        max_results_per_source=3,
        include_sources=["news", "web", "reddit", "wikipedia"],
    )

    result = await graph.ainvoke(initial, CONFIG)

    assert result["status"] in ("completed", "partial")
    assert "report_markdown" in result
    assert len(result["report_markdown"]) > 0
    assert "extracted_evidence" in result


@pytest.mark.asyncio
async def test_graph_empty_question() -> None:
    graph = build_graph(checkpointer=True)
    initial = ResearchState(question="")
    result = await graph.ainvoke(initial, CONFIG)
    assert result["status"] == "failed"
    assert "errors" in result


@pytest.mark.asyncio
async def test_graph_partial_sources() -> None:
    graph = build_graph(checkpointer=True)
    initial = ResearchState(
        question="Test question",
        include_sources=["news"],
        max_results_per_source=2,
    )
    result = await graph.ainvoke(initial, CONFIG)
    assert result["status"] in ("completed", "partial")
    assert "report_markdown" in result

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage

from pocket_powered_analyser.graph.builder import build_graph
from pocket_powered_analyser.state.schema import AgentState


@pytest.mark.asyncio
async def test_graph_invocation() -> None:
    graph = build_graph()
    result = await graph.ainvoke(
        {"messages": [HumanMessage(content="Say 'hello world'")]},
    )
    assert "messages" in result
    assert len(result["messages"]) > 0

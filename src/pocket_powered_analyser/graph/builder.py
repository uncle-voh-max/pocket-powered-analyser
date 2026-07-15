from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from pocket_powered_analyser.nodes.agent import call_agent, should_continue
from pocket_powered_analyser.state.schema import AgentState


def build_graph() -> CompiledStateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_agent)
    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "agent", "respond": END},
    )

    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)

from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from research_agent.graph.edges import (
    should_continue_after_extraction,
    should_continue_after_fetch,
    should_continue_to_search,
)
from research_agent.graph.nodes import (
    analyse_evidence_node,
    deduplicate_evidence_node,
    extract_evidence_node,
    fallback_search,
    fetch_documents,
    generate_report_node,
    persist_run,
    plan_queries_node,
    score_reliability_node,
    search_news,
    search_reddit,
    search_social,
    search_web,
    search_wikipedia,
    validate_request,
)
from research_agent.graph.state import ResearchState


def build_graph(checkpointer: bool = True) -> CompiledStateGraph:
    workflow = StateGraph(ResearchState)

    # Core pipeline
    workflow.add_node("validate_request", validate_request)
    workflow.add_node("plan_queries", plan_queries_node)
    workflow.add_node("search_news", search_news)
    workflow.add_node("search_web", search_web)
    workflow.add_node("search_social", search_social)
    workflow.add_node("search_reddit", search_reddit)
    workflow.add_node("search_wikipedia", search_wikipedia)
    workflow.add_node("fetch_documents", fetch_documents)
    workflow.add_node("extract_evidence", extract_evidence_node)
    workflow.add_node("deduplicate_evidence", deduplicate_evidence_node)
    workflow.add_node("score_reliability", score_reliability_node)
    workflow.add_node("analyse_evidence", analyse_evidence_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("persist_run", persist_run)

    # Recovery
    workflow.add_node("fallback_search", fallback_search)

    # Entry point
    workflow.set_entry_point("validate_request")

    # Flow
    workflow.add_edge("validate_request", "plan_queries")

    workflow.add_conditional_edges(
        "plan_queries",
        should_continue_to_search,
        {
            "parallel_search": "search_news",
            "end": END,
        },
    )

    # Parallel search fan-out
    for source_node in ["search_news", "search_web", "search_social", "search_reddit", "search_wikipedia"]:
        workflow.add_edge(source_node, "fetch_documents")

    workflow.add_conditional_edges(
        "fetch_documents",
        should_continue_after_fetch,
        {"extract": "extract_evidence", "fallback": "fallback_search"},
    )

    # fallback_search -> rejoin the main pipeline at dedup (break the loop)
    workflow.add_edge("fallback_search", "deduplicate_evidence")

    workflow.add_conditional_edges(
        "extract_evidence",
        should_continue_after_extraction,
        {"analyse": "deduplicate_evidence", "fallback": "deduplicate_evidence"},
    )

    workflow.add_edge("deduplicate_evidence", "score_reliability")
    workflow.add_edge("score_reliability", "analyse_evidence")
    workflow.add_edge("analyse_evidence", "generate_report")
    workflow.add_edge("generate_report", "persist_run")
    workflow.add_edge("persist_run", END)

    if checkpointer:
        return workflow.compile(checkpointer=MemorySaver())
    return workflow.compile()

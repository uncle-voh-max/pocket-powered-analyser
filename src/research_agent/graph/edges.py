from __future__ import annotations

from research_agent.graph.state import ResearchState


def should_continue_to_search(state: ResearchState) -> str:
    if state.status == "failed":
        return "end"
    return "parallel_search"


def should_continue_after_fetch(state: ResearchState) -> str:
    if not state.raw_documents and state.errors:
        return "fallback"
    return "extract"


def should_continue_after_extraction(state: ResearchState) -> str:
    if not state.extracted_evidence:
        return "fallback"
    return "analyse"

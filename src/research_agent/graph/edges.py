from __future__ import annotations

from research_agent.graph.state import ResearchState
from langgraph.graph import END
from typing import Literal


def should_continue_to_search(state: ResearchState) -> list[str] | str :
    if state.status == "failed":
        return END
    return [
    "search_news",
    "search_web",
    "search_social",
    "search_reddit",
    "search_wikipedia"
    ]



def should_continue_after_fetch(state: ResearchState) -> str:
    if not state.raw_documents and state.errors:
        return "fallback"
    return "extract"


def should_continue_after_extraction(state: ResearchState) -> str:
    if not state.extracted_evidence:
        return "fallback"
    return "analyse"

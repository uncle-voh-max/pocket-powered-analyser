from __future__ import annotations

from typing import Annotated, Any

from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep
from pydantic import BaseModel, Field

from research_agent.adapters.base import RawDocument, RawSearchResult
from research_agent.analysis.synthesis import SynthesisResult
from research_agent.extraction.extractor import ExtractedEvidence
from research_agent.planning.query_planner import QueryPlan


class ResearchState(BaseModel):
    # Input
    question: str = ""
    max_results_per_source: int = Field(default=10)
    include_sources: list[str] = Field(default_factory=lambda: ["news", "web", "reddit", "wikipedia"])
    time_window_days: int = Field(default=30)

    # Pipeline outputs
    query_plan: QueryPlan | None = None
    raw_search_results: dict[str, list[RawSearchResult]] = Field(default_factory=dict)
    raw_documents: list[RawDocument] = Field(default_factory=list)
    extracted_evidence: list[ExtractedEvidence] = Field(default_factory=list)
    synthesis: SynthesisResult | None = None
    report_markdown: str = ""
    report_json: str = ""

    # Runtime
    run_id: str = ""
    status: str = "pending"
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    iteration_count: int = 0

    # LangGraph managed
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    is_last_step: IsLastStep = False

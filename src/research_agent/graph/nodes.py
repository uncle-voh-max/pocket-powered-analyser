from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from research_agent.adapters.base import BaseSearchAdapter, RawDocument, RawSearchResult
from research_agent.adapters.mock import get_mock_adapter
from research_agent.adapters.news import NewsSearchAdapter
from research_agent.adapters.reddit import RedditSearchAdapter
from research_agent.adapters.social import SocialSearchAdapter
from research_agent.adapters.web import WebSearchAdapter
from research_agent.adapters.wikipedia import WikipediaSearchAdapter
from research_agent.analysis.analyser import analyse_evidence
from research_agent.analysis.dedupe import deduplicate_evidence
from research_agent.analysis.reliability import score_source_reliability
from research_agent.extraction.extractor import extract_evidence
from research_agent.graph.state import ResearchState
from research_agent.logging import logger
from research_agent.planning.query_planner import QueryPlan, plan_queries
from research_agent.report.markdown import generate_markdown_report
from research_agent.storage.repository import ResearchRunRecord
from research_agent.storage.jsonl_repository import JSONLRepository


async def validate_request(state: ResearchState) -> dict[str, Any]:
    if not state.question or not state.question.strip():
        return {"errors": ["Question is empty"], "status": "failed"}
    return {
        "run_id": f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "status": "planning",
    }


async def plan_queries_node(state: ResearchState) -> dict[str, Any]:
    if state.status == "failed":
        logger.info("skipping_planning", reason="validation_failed")
        return {}
    logger.info("planning_queries", question=state.question)
    try:
        plan = await plan_queries(state.question)
        return {"query_plan": plan, "status": "searching"}
    except Exception as e:
        logger.error("planning_failed", error=str(e))
        return {
            "query_plan": QueryPlan(
                original_question=state.question,
                research_objective=state.question,
            ),
            "errors": [f"Query planning failed: {e}"],
            "status": "searching",
        }


def _get_adapter(source_type: str) -> BaseSearchAdapter:
    adapters = {
        "news": NewsSearchAdapter(),
        "web": WebSearchAdapter(),
        "reddit": RedditSearchAdapter(),
        "social": SocialSearchAdapter(),
        "wikipedia": WikipediaSearchAdapter(),
    }
    return adapters.get(source_type) or get_mock_adapter(source_type)


async def _search_source(
    source_type: str,
    plan: QueryPlan | None,
    max_results: int = 10,
) -> list[RawSearchResult]:
    empty_plan = QueryPlan(original_question="", research_objective="")
    qp = plan or empty_plan

    adapter = _get_adapter(source_type)
    results = await adapter.search(qp.search_plan, max_results=max_results)
    logger.info("source_search_complete", source=source_type, count=len(results))
    return results


async def search_news(state: ResearchState) -> dict[str, Any]:
    results = await _search_source("news", state.query_plan, max_results=state.max_results_per_source)
    return {"raw_search_results": {"news": results}}


async def search_web(state: ResearchState) -> dict[str, Any]:
    results = await _search_source("web", state.query_plan, max_results=state.max_results_per_source)
    return {"raw_search_results": {"web": results}}


async def search_social(state: ResearchState) -> dict[str, Any]:
    results = await _search_source("social", state.query_plan, max_results=state.max_results_per_source)
    return {"raw_search_results": {"social": results}}


async def search_reddit(state: ResearchState) -> dict[str, Any]:
    results = await _search_source("reddit", state.query_plan, max_results=state.max_results_per_source)
    return {"raw_search_results": {"reddit": results}}


async def search_wikipedia(state: ResearchState) -> dict[str, Any]:
    results = await _search_source("wikipedia", state.query_plan, max_results=state.max_results_per_source)
    return {"raw_search_results": {"wikipedia": results}}


async def fetch_documents(state: ResearchState) -> dict[str, Any]:
    all_results: list[RawSearchResult] = []
    for results in state.raw_search_results.values():
        all_results.extend(results)
    documents: list[RawDocument] = []
    for result in all_results:
        adapter = _get_adapter(result.source_type)
        try:
            doc = await adapter.fetch(result)
            documents.append(doc)
        except Exception as e:
            logger.warning("fetch_failed", url=result.url, error=str(e))

    logger.info("documents_fetched", count=len(documents))
    return {"raw_documents": documents}


async def extract_evidence_node(state: ResearchState) -> dict[str, Any]:
    evidence: list[ExtractedEvidence] = []
    for doc in state.raw_documents:
        try:
            ev = await extract_evidence(doc, doc.source_type)
            evidence.append(ev)
        except Exception as e:
            logger.warning("extraction_failed", url=doc.url, error=str(e))

    logger.info("evidence_extracted", count=len(evidence))
    return {"extracted_evidence": evidence}


async def deduplicate_evidence_node(state: ResearchState) -> dict[str, Any]:
    deduped = deduplicate_evidence(state.extracted_evidence)
    logger.info("deduplication_complete", before=len(state.extracted_evidence), after=len(deduped))
    return {"extracted_evidence": deduped}


async def score_reliability_node(state: ResearchState) -> dict[str, Any]:
    for ev in state.extracted_evidence:
        reliability = score_source_reliability(ev)
        for claim in ev.claims:
            claim.source_reliability = reliability
    return {}


async def analyse_evidence_node(state: ResearchState) -> dict[str, Any]:
    try:
        synthesis = await analyse_evidence(state.extracted_evidence)
        return {"synthesis": synthesis}
    except Exception as e:
        logger.error("analysis_failed", error=str(e))
        return {"errors": [f"Cross-source analysis failed: {e}"]}


async def generate_report_node(state: ResearchState) -> dict[str, Any]:
    try:
        report = generate_markdown_report(
            question=state.question,
            query_plan=state.query_plan,
            evidence=state.extracted_evidence,
            synthesis=state.synthesis,
            warnings=state.warnings,
        )
        return {"report_markdown": report, "status": "completed"}
    except Exception as e:
        logger.error("report_generation_failed", error=str(e))
        return {
            "report_markdown": f"# Research Report\n\nReport generation failed: {e}",
            "status": "partial",
            "errors": [f"Report generation failed: {e}"],
        }


async def persist_run(state: ResearchState) -> dict[str, Any]:
    try:
        repo = JSONLRepository()
        run = ResearchRunRecord(
            run_id=state.run_id,
            question=state.question,
            status=state.status,
            report_markdown=state.report_markdown,
            evidence_count=len(state.extracted_evidence),
            warnings=state.warnings,
        )
        await repo.save_run(run)
    except Exception as e:
        logger.warning("persist_failed", error=str(e))
    return {}


async def fallback_search(state: ResearchState) -> dict[str, Any]:
    """Fallback to mock adapters when real adapters fail."""
    missing = [s for s in state.include_sources if s not in state.raw_search_results]
    for source in missing:
        mock = get_mock_adapter(source)
        results = await mock.search(
            state.query_plan.search_plan if state.query_plan else None,  # type: ignore[arg-type]
            max_results=state.max_results_per_source,
        )
        state.raw_search_results[source] = results
    return {}

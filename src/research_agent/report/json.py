from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from research_agent.analysis.reliability import score_source_reliability
from research_agent.analysis.synthesis import SynthesisResult
from research_agent.extraction.extractor import ExtractedEvidence
from research_agent.planning.query_planner import QueryPlan


def generate_json_report(
    question: str,
    query_plan: QueryPlan | None,
    evidence: list[ExtractedEvidence],
    synthesis: SynthesisResult | None,
    warnings: list[str],
) -> str:
    report: dict[str, Any] = {
        "report_type": "research_report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "evidence_count": len(evidence),
        "warnings": warnings,
    }

    if query_plan:
        report["query_plan"] = query_plan.model_dump()

    if synthesis:
        report["synthesis"] = synthesis.model_dump()

    report["evidence"] = []
    for ev in evidence:
        ev_dict = ev.model_dump()
        ev_dict["reliability"] = score_source_reliability(ev)
        report["evidence"].append(ev_dict)

    return json.dumps(report, indent=2, default=str)

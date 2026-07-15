from __future__ import annotations

from datetime import datetime, timezone

from research_agent.analysis.reliability import score_source_reliability
from research_agent.analysis.synthesis import SynthesisResult
from research_agent.extraction.extractor import ExtractedEvidence
from research_agent.planning.query_planner import QueryPlan


def generate_markdown_report(
    question: str,
    query_plan: QueryPlan | None,
    evidence: list[ExtractedEvidence],
    synthesis: SynthesisResult | None,
    warnings: list[str],
) -> str:
    lines: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines.append(f"# Research Report: {question}\n")
    lines.append(f"*Generated: {ts}*  \n")
    lines.append(f"*Evidence items: {len(evidence)}*  \n")
    if warnings:
        lines.append(f"*Warnings: {len(warnings)}*  \n")
    lines.append("")

    # Executive summary
    lines.append("## Executive Summary\n")
    if synthesis:
        lines.append(synthesis.summary or "See key findings below.\n")
    else:
        lines.append("Analysis completed.\n")

    # Key findings
    lines.append("## Key Findings\n")
    if synthesis:
        if synthesis.major_themes:
            lines.append("### Major Themes\n")
            for t in synthesis.major_themes:
                lines.append(f"- {t}")
            lines.append("")
        if synthesis.well_supported:
            lines.append("### Well-Supported Conclusions\n")
            for c in synthesis.well_supported:
                lines.append(f"- {c}")
            lines.append("")
        if synthesis.weakly_supported:
            lines.append("### Weakly Supported\n")
            for c in synthesis.weakly_supported:
                lines.append(f"- {c}")
            lines.append("")
        if synthesis.contradictions:
            lines.append("### Contradictions\n")
            for c in synthesis.contradictions:
                lines.append(f"- {c}")
            lines.append("")
        if synthesis.repeated_claims:
            lines.append("### Corroborated Claims\n")
            for c in synthesis.repeated_claims:
                lines.append(f"- {c}")
            lines.append("")

    # Evidence table
    lines.append("## Evidence Table\n")
    lines.append("| # | Source Type | Title | Reliability | Key Claims |")
    lines.append("|---|------------|-------|-------------|------------|")
    for i, ev in enumerate(evidence, 1):
        reliability = score_source_reliability(ev)
        claims_summary = "; ".join(c.claim[:60] for c in ev.claims[:2])
        lines.append(
            f"| {i} | {ev.source_type} | [{ev.title[:50]}]({ev.url}) "
            f"| {reliability:.2f} | {claims_summary} |"
        )
    lines.append("")

    # Source reliability notes
    lines.append("## Source Reliability Notes\n")
    lines.append("| Source | Count | Avg Reliability | Notes |")
    lines.append("|--------|-------|-----------------|-------|")
    by_type: dict[str, list[ExtractedEvidence]] = {}
    for ev in evidence:
        by_type.setdefault(ev.source_type, []).append(ev)
    for st, items in sorted(by_type.items()):
        avg_rel = sum(score_source_reliability(i) for i in items) / len(items)
        notes = _reliability_note(st)
        lines.append(f"| {st} | {len(items)} | {avg_rel:.2f} | {notes} |")
    lines.append("")

    # Contradictions
    if synthesis and synthesis.contradictions:
        lines.append("## Contradictions and Uncertainty\n")
        for c in synthesis.contradictions:
            lines.append(f"- {c}")
        lines.append("")

    # Per-source summaries
    lines.append("## Per-Source Summaries\n")
    for i, ev in enumerate(evidence, 1):
        reliability = score_source_reliability(ev)
        lines.append(f"### {i}. {ev.title}")
        lines.append(f"- **Source**: [{ev.url}]({ev.url})")
        lines.append(f"- **Type**: {ev.source_type}")
        lines.append(f"- **Publisher**: {ev.publisher_or_platform}")
        lines.append(f"- **Reliability**: {reliability:.2f}")
        if ev.summary:
            lines.append(f"- **Summary**: {ev.summary}")
        if ev.key_points:
            lines.append("- **Key Points**:")
            for kp in ev.key_points[:5]:
                lines.append(f"  - {kp}")
        if ev.claims:
            lines.append("- **Claims**:")
            for c in ev.claims[:5]:
                lines.append(
                    f"  - {c.claim[:100]} "
                    f"(conf: {c.confidence:.1f}, verify: {c.requires_verification})"
                )
        if ev.limitations:
            lines.append(f"- **Limitations**: {'; '.join(ev.limitations)}")
        lines.append("")

    # Research gaps
    if synthesis:
        lines.append("## Recommendations for Further Research\n")
        if synthesis.requires_more_research:
            for r in synthesis.requires_more_research:
                lines.append(f"- {r}")
        if synthesis.missing_sources:
            for m in synthesis.missing_sources:
                lines.append(f"- Missing source: {m}")
        lines.append("")

    # Appendix
    lines.append("## Appendix\n")
    lines.append(f"- **Research question**: {question}")
    if query_plan:
        lines.append(f"- **Time sensitivity**: {query_plan.time_sensitivity}")
        if query_plan.entities:
            lines.append(f"- **Entities identified**: {', '.join(query_plan.entities)}")
        if query_plan.constraints:
            lines.append(f"- **Constraints**: {'; '.join(query_plan.constraints)}")
    lines.append("")

    if warnings:
        lines.append("## Warnings\n")
        for w in warnings:
            lines.append(f"- ⚠ {w}")
        lines.append("")

    return "\n".join(lines)


def _reliability_note(source_type: str) -> str:
    notes = {
        "news": "Medium-high if established publisher",
        "web": "Varies by domain authority",
        "wikipedia": "Background reference, not primary",
        "reddit": "Anecdotal; low reliability",
        "social": "Low reliability; needs corroboration",
    }
    return notes.get(source_type, "Unknown")

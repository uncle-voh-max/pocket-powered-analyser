from __future__ import annotations

from research_agent.analysis.synthesis import SynthesisResult
from research_agent.analysis.reliability import score_source_reliability
from research_agent.analysis.dedupe import deduplicate_evidence, group_by_source_type
from research_agent.extraction.extractor import ExtractedEvidence
from research_agent.llm.client import llm_call

SYNTHESIS_SYSTEM_PROMPT = """You are a senior research analyst.

Given a collection of extracted evidence from multiple sources, produce a synthesis.

Identify:
1. Major themes that appear across multiple sources.
2. Claims that are repeated across independent sources (corroborated).
3. Contradictions or conflicting claims between sources.
4. What is well-supported by high-quality evidence.
5. What is weakly supported or based on low-reliability sources.
6. What requires more research.
7. What sources were missing or inaccessible.

Consider source reliability when weighting evidence. Social/Reddit evidence should
be treated as anecdotal unless corroborated by authoritative sources."""

SYNTHESIS_USER_PROMPT = """Evidence summary:
{evidence_summary}

Produce a structured synthesis as a JSON object."""


async def analyse_evidence(
    evidence_items: list[ExtractedEvidence],
) -> SynthesisResult:
    deduped = deduplicate_evidence(evidence_items)
    for item in deduped:
        item.claims  # ensure claims loaded

    # Score reliability
    for item in deduped:
        reliability = score_source_reliability(item)
        for claim in item.claims:
            claim.source_reliability = reliability

    by_type = group_by_source_type(deduped)

    evidence_summary = _build_summary(deduped, by_type)

    try:
        result = await llm_call(
            system_prompt=SYNTHESIS_SYSTEM_PROMPT,
            user_prompt=SYNTHESIS_USER_PROMPT.format(evidence_summary=evidence_summary),
            response_model=SynthesisResult,
            max_retries=2,
        )
    except Exception:
        result = SynthesisResult(
            major_themes=["Analysis failed — using default synthesis"],
            summary="Synthesis could not be completed due to an error.",
        )

    return result


def _build_summary(
    items: list[ExtractedEvidence],
    by_type: dict[str, list[ExtractedEvidence]],
) -> str:
    lines = [f"Total evidence items: {len(items)}"]
    for source_type, group in by_type.items():
        lines.append(f"\n--- {source_type.upper()} ({len(group)} items) ---")
        for ev in group[:5]:
            reliability = score_source_reliability(ev)
            lines.append(f"  - {ev.title[:80]} (reliability: {reliability:.2f})")
            for claim in ev.claims[:3]:
                lines.append(f"    Claim: {claim.claim[:100]} (conf: {claim.confidence:.2f})")

    return "\n".join(lines)

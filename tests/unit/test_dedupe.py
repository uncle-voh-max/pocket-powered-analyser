from __future__ import annotations

from research_agent.analysis.dedupe import deduplicate_evidence, group_by_source_type
from research_agent.extraction.extractor import ExtractedEvidence


def test_deduplicate_by_url() -> None:
    items = [
        ExtractedEvidence(title="A", url="https://example.com/page"),
        ExtractedEvidence(title="B", url="https://example.com/page"),
        ExtractedEvidence(title="C", url="https://example.com/other"),
    ]
    deduped = deduplicate_evidence(items)
    assert len(deduped) == 2


def test_deduplicate_by_similar_title() -> None:
    items = [
        ExtractedEvidence(title="Breaking News About AI Safety"),
        ExtractedEvidence(title="Breaking News About AI Safety Today"),
        ExtractedEvidence(title="Something Completely Different"),
    ]
    deduped = deduplicate_evidence(items)
    # Jaccard similarity between first two is 5/6=0.833 > 0.8, so they dedupe
    assert len(deduped) == 2


def test_deduplicate_with_dissimilar_titles() -> None:
    items = [
        ExtractedEvidence(title="Completely Different Topic"),
        ExtractedEvidence(title="Something Unrelated Here"),
    ]
    deduped = deduplicate_evidence(items)
    assert len(deduped) == 2


def test_deduplicate_empty() -> None:
    assert deduplicate_evidence([]) == []


def test_group_by_source_type() -> None:
    items = [
        ExtractedEvidence(source_type="news"),
        ExtractedEvidence(source_type="web"),
        ExtractedEvidence(source_type="news"),
    ]
    groups = group_by_source_type(items)
    assert len(groups["news"]) == 2
    assert len(groups["web"]) == 1


def test_canonical_url_dedupe() -> None:
    items = [
        ExtractedEvidence(title="A", url="https://Example.com/Page"),
        ExtractedEvidence(title="B", url="https://example.com/page"),
    ]
    deduped = deduplicate_evidence(items)
    assert len(deduped) == 1

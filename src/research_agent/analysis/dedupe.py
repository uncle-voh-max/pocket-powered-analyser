from __future__ import annotations

from research_agent.extraction.extractor import ExtractedEvidence
from research_agent.utils.urls import canonicalise
from research_agent.utils.hashing import title_similarity


def deduplicate_evidence(items: list[ExtractedEvidence]) -> list[ExtractedEvidence]:
    """Remove duplicate evidence by URL, canonical URL, and near-identical title."""
    seen_urls: set[str] = set()
    seen_titles: list[str] = []
    deduped: list[ExtractedEvidence] = []

    for item in items:
        # URL dedup: skip only if URL is non-empty and canonicalised match
        if item.url:
            canon = canonicalise(item.url)
            if canon in seen_urls:
                continue
            seen_urls.add(canon)

        # Title similarity check
        is_dup_title = False
        for seen in seen_titles:
            if title_similarity(item.title, seen) > 0.8:
                is_dup_title = True
                break

        if is_dup_title:
            continue

        seen_titles.append(item.title)
        deduped.append(item)

    return deduped


def group_by_source_type(items: list[ExtractedEvidence]) -> dict[str, list[ExtractedEvidence]]:
    groups: dict[str, list[ExtractedEvidence]] = {}
    for item in items:
        groups.setdefault(item.source_type, []).append(item)
    return groups

from __future__ import annotations

from datetime import datetime, timezone

from research_agent.extraction.extractor import ExtractedEvidence

# Domain reputation heuristics
HIGH_REPUTATION_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "nytimes.com", "wsj.com", "economist.com", "ft.com",
    "nature.com", "science.org", "sciencedirect.com",
    "who.int", "un.org", "worldbank.org", "gov",
    "edu", "nih.gov", "cdc.gov",
}

MEDIUM_REPUTATION_DOMAINS = {
    "theguardian.com", "washingtonpost.com", "bloomberg.com",
    "cnn.com", "npr.org", "pbs.org", "forbes.com",
    "techcrunch.com", "wired.com", "arstechnica.com",
    "theverge.com", "medium.com",
}


def score_source_reliability(evidence: ExtractedEvidence) -> float:
    """Score 0.0 - 1.0 based on source characteristics."""
    score = 0.5  # baseline

    source_type = evidence.source_type
    publisher = evidence.publisher_or_platform.lower()
    has_author = bool(evidence.author)

    # Source type factors
    type_scores = {
        "news": 0.6,
        "web": 0.5,
        "wikipedia": 0.4,
        "reddit": 0.15,
        "social": 0.1,
    }
    score = type_scores.get(source_type, 0.3)

    # Domain reputation
    for domain in HIGH_REPUTATION_DOMAINS:
        if domain in publisher or publisher.endswith(f".{domain}"):
            score += 0.25
            break
    else:
        for domain in MEDIUM_REPUTATION_DOMAINS:
            if domain in publisher:
                score += 0.1
                break

    # Author presence
    if has_author:
        score += 0.05

    # Recency
    if evidence.published_at:
        try:
            pub = datetime.fromisoformat(evidence.published_at.replace("Z", "+00:00"))
            days_old = (datetime.now(timezone.utc) - pub).days
            if days_old > 365 * 2:
                score -= 0.15
            elif days_old > 365:
                score -= 0.05
        except (ValueError, TypeError):
            pass

    # Sentiment factor (opinion-heavy content less reliable)
    if evidence.sentiment in ("positive", "negative") and source_type in ("news", "web"):
        score -= 0.05

    # Claims factor: more verifiable claims = better
    if evidence.claims:
        avg_confidence = sum(c.confidence for c in evidence.claims) / len(evidence.claims)
        score = score * 0.7 + avg_confidence * 0.3

    return max(0.0, min(1.0, score))

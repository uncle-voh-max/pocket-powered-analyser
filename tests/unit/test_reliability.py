from __future__ import annotations

from research_agent.analysis.reliability import score_source_reliability
from research_agent.extraction.extractor import Claim, ExtractedEvidence


def test_high_reliability_news() -> None:
    ev = ExtractedEvidence(
        source_type="news",
        publisher_or_platform="reuters.com",
        author="John Smith",
        claims=[Claim(claim="Test", confidence=0.9, source_reliability=0.0)],
    )
    score = score_source_reliability(ev)
    assert score > 0.5


def test_low_reliability_social() -> None:
    ev = ExtractedEvidence(
        source_type="social",
        publisher_or_platform="twitter.com",
        claims=[Claim(claim="Test", confidence=0.3, source_reliability=0.0)],
    )
    score = score_source_reliability(ev)
    assert score < 0.5


def test_medium_reliability_wikipedia() -> None:
    ev = ExtractedEvidence(
        source_type="wikipedia",
        publisher_or_platform="wikipedia.org",
    )
    score = score_source_reliability(ev)
    assert 0.3 <= score <= 0.6


def test_reliability_no_claims() -> None:
    ev = ExtractedEvidence(
        source_type="web",
        publisher_or_platform="example.com",
    )
    score = score_source_reliability(ev)
    assert 0.0 <= score <= 1.0


def test_reliability_gov_domain() -> None:
    ev = ExtractedEvidence(
        source_type="web",
        publisher_or_platform="cdc.gov",
        claims=[Claim(claim="Test", confidence=0.9, source_reliability=0.0)],
    )
    score = score_source_reliability(ev)
    assert score > 0.6

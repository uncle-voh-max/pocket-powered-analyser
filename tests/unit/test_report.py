from __future__ import annotations

from research_agent.analysis.synthesis import SynthesisResult
from research_agent.extraction.extractor import ExtractedEvidence
from research_agent.planning.query_planner import QueryPlan, SearchPlan
from research_agent.report.markdown import generate_markdown_report


def test_markdown_report_generation() -> None:
    report = generate_markdown_report(
        question="What is the impact of AI?",
        query_plan=QueryPlan(
            original_question="What is the impact of AI?",
            research_objective="Analyse AI impact",
            time_sensitivity="evergreen",
            entities=["AI", "machine learning"],
            search_plan=SearchPlan(news=["AI impact"], web=["AI impact"]),
        ),
        evidence=[
            ExtractedEvidence(
                source_type="news",
                title="AI Impact Study",
                url="https://example.com/ai",
                summary="AI has significant impact.",
                key_points=["Automation", "Productivity"],
                claims=[],
                sentiment="neutral",
            ),
        ],
        synthesis=SynthesisResult(
            major_themes=["Economic transformation"],
            well_supported=["AI drives productivity"],
            summary="AI is transforming industries.",
        ),
        warnings=["Limited sources"],
    )
    assert isinstance(report, str)
    assert "Research Report" in report
    assert "What is the impact of AI?" in report
    assert "Economic transformation" in report
    assert "Limited sources" in report
    assert "AI Impact Study" in report


def test_markdown_report_empty_evidence() -> None:
    report = generate_markdown_report(
        question="Test question",
        query_plan=None,
        evidence=[],
        synthesis=None,
        warnings=[],
    )
    assert "Test question" in report
    assert "0" in report


def test_markdown_report_no_synthesis() -> None:
    report = generate_markdown_report(
        question="Test",
        query_plan=None,
        evidence=[ExtractedEvidence(title="Test", url="https://example.com")],
        synthesis=None,
        warnings=[],
    )
    assert "Test" in report

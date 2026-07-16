from __future__ import annotations

from prometheus_client import Counter, Histogram

research_runs_total = Counter(
    "research_runs_total",
    "Total research runs",
    ["status"],
)

research_run_duration_seconds = Histogram(
    "research_run_duration_seconds",
    "Duration of research runs in seconds",
    buckets=[1, 5, 10, 30, 60, 120, 300, 600],
)

source_search_duration_seconds = Histogram(
    "source_search_duration_seconds",
    "Duration of source searches in seconds",
    ["source"],
    buckets=[0.5, 1, 2, 5, 10, 30],
)

source_search_failures_total = Counter(
    "source_search_failures_total",
    "Total source search failures",
    ["source"],
)

llm_calls_total = Counter(
    "llm_calls_total",
    "Total LLM calls",
    ["operation"],
)

llm_failures_total = Counter(
    "llm_failures_total",
    "Total LLM failures",
    ["operation"],
)

documents_fetched_total = Counter(
    "documents_fetched_total",
    "Total documents fetched",
    ["source_type"],
)

evidence_items_extracted_total = Counter(
    "evidence_items_extracted_total",
    "Total evidence items extracted",
)

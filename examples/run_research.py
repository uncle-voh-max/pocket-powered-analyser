#!/usr/bin/env python
"""Example: Run a research workflow with a sample question using mock adapters.

Usage:
    uv run python examples/run_research.py
"""

from __future__ import annotations

import asyncio

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from research_agent.config import settings
from research_agent.graph.state import ResearchState
from research_agent.graph.workflow import build_graph
from research_agent.logging import setup_logging

load_dotenv()
setup_logging(debug=settings.debug)
console = Console()


async def main() -> None:
    question = "What are the key developments in AI agent safety for 2026?"

    console.print(f"[bold]Research question:[/] {question}\n")

    graph = build_graph()
    initial = ResearchState(
        question=question,
        max_results_per_source=3,
        include_sources=["news", "web", "reddit", "wikipedia"],
    )

    with console.status("[bold green]Running research workflow..."):
        result = await graph.ainvoke(
            initial,
            {"configurable": {"thread_id": "example"}},
        )

    status = result.get("status", "unknown")
    evidence_count = len(result.get("extracted_evidence", []))
    warnings = result.get("warnings", [])

    console.print(f"\n[bold]Status:[/] {status}")
    console.print(f"[bold]Evidence items:[/] {evidence_count}")

    if warnings:
        console.print("\n[bold yellow]Warnings:[/]")
        for w in warnings:
            console.print(f"  - {w}")

    report = result.get("report_markdown", "")
    if report:
        md = Markdown(report)
        console.print(md)


if __name__ == "__main__":
    asyncio.run(main())

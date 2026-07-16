from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from research_agent.config import settings
from research_agent.graph.state import ResearchState
from research_agent.graph.workflow import build_graph
from research_agent.logging import setup_logging
from research_agent.storage.jsonl_repository import JSONLRepository

cli = typer.Typer(
    name="research-agent",
    help="Production-grade agentic research platform",
    no_args_is_help=True,
)
console = Console()


@cli.command()
def run(
    question: Optional[str] = typer.Argument(None, help="Research question"),
    question_file: Optional[Path] = typer.Option(
        None, "--question-file", "-f",
        help="Read question from a file",
        exists=True,
        readable=True,
    ),
    include: str = typer.Option(
        "news,web,reddit,wikipedia",
        "--include",
        help="Comma-separated list of sources to include",
    ),
    max_results: int = typer.Option(
        10, "--max-results", "-n",
        help="Max results per source",
        min=1,
        max=50,
    ),
    days: int = typer.Option(
        30, "--days", "-d",
        help="Time window in days",
        min=1,
        max=365,
    ),
    format: str = typer.Option(
        "markdown",
        "--format",
        help="Output format",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Write report to file instead of stdout",
    ),
) -> None:
    """Run a full research workflow."""
    if question is None and question_file is not None:
        question = question_file.read_text().strip()
    if question is None:
        console.print("[red]Error:[/] Either a question or --question-file is required.")
        raise typer.Exit(1)

    setup_logging(debug=settings.debug)
    sources = [s.strip() for s in include.split(",") if s.strip()]

    async def _run() -> dict:
        graph = build_graph()
        initial = ResearchState(
            question=question,
            max_results_per_source=max_results,
            include_sources=sources,
            time_window_days=days,
        )
        return await graph.ainvoke(
            initial,
            {"configurable": {"thread_id": "cli_run"}},
        )

    with console.status("[bold green]Running research workflow..."):
        result = asyncio.run(_run())

    report = result.get("report_markdown", "")
    status = result.get("status", "unknown")
    evidence_count = len(result.get("extracted_evidence", []))
    warnings = result.get("warnings", [])

    console.print(f"\n[bold]Status:[/] {status}")
    console.print(f"[bold]Evidence items:[/] {evidence_count}")
    if warnings:
        console.print("[bold yellow]Warnings:[/]")
        for w in warnings:
            console.print(f"  - {w}")

    if format == "json":
        from research_agent.report.json import generate_json_report
        json_report = generate_json_report(
            question=question,
            query_plan=result.get("query_plan"),
            evidence=result.get("extracted_evidence", []),
            synthesis=result.get("synthesis"),
            warnings=warnings,
        )
        if output:
            output.write_text(json_report)
            console.print(f"\n[green]Report written to:[/] {output}")
        else:
            console.print(json_report)
    else:
        if output:
            output.write_text(report)
            console.print(f"\n[green]Report written to:[/] {output}")
        else:
            md = Markdown(report)
            console.print(md)


@cli.command()
def show_run(
    run_id: str = typer.Argument(..., help="Run ID to display"),
) -> None:
    """Show details of a completed research run."""
    async def _get() -> dict | None:
        repo = JSONLRepository()
        run = await repo.get_run(run_id)
        if run is None:
            return None
        return {
            "run_id": run.run_id,
            "question": run.question,
            "status": run.status,
            "evidence_count": run.evidence_count,
            "warnings": run.warnings,
        }

    result = asyncio.run(_get())
    if result is None:
        console.print(f"[red]Run not found:[/] {run_id}")
        raise typer.Exit(1)

    console.print(f"[bold]Run ID:[/] {result['run_id']}")
    console.print(f"[bold]Question:[/] {result['question']}")
    console.print(f"[bold]Status:[/] {result['status']}")
    console.print(f"[bold]Evidence count:[/] {result['evidence_count']}")
    if result.get("warnings"):
        console.print("[bold yellow]Warnings:[/]")
        for w in result["warnings"]:
            console.print(f"  - {w}")


@cli.command()
def export(
    run_id: str = typer.Argument(..., help="Run ID to export"),
    format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Export format: markdown or json",
    ),
    output: Path = typer.Option(
        ...,
        "--output",
        "-o",
        help="Output file path",
    ),
) -> None:
    """Export a completed run's report."""
    async def _export() -> None:
        repo = JSONLRepository()
        run = await repo.get_run(run_id)
        if run is None:
            console.print(f"[red]Run not found:[/] {run_id}")
            raise typer.Exit(1)
        output.write_text(run.report_markdown)
        console.print(f"[green]Report exported to:[/] {output}")

    asyncio.run(_export())


if __name__ == "__main__":
    cli()

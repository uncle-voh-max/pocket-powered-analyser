from __future__ import annotations

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import REGISTRY, generate_latest
from pydantic import BaseModel, Field

from research_agent.config import settings
from research_agent.graph.state import ResearchState
from research_agent.graph.workflow import build_graph
from research_agent.logging import logger, setup_logging
from research_agent.observability import metrics
from research_agent.storage.jsonl_repository import JSONLRepository


class ResearchRequest(BaseModel):
    question: str
    max_results_per_source: int = Field(default=10, ge=1, le=50)
    include_sources: list[str] = Field(
        default_factory=lambda: ["news", "web", "reddit", "wikipedia"],
    )
    time_window_days: int = Field(default=30, ge=1, le=365)
    report_format: str = Field(default="markdown", pattern="^(markdown|json)$")


class ResearchResponse(BaseModel):
    run_id: str
    status: str
    report_markdown: str = ""
    evidence_count: int = 0
    warnings: list[str] = Field(default_factory=list)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    setup_logging(debug=settings.debug)
    logger.info("research_agent_startup")
    yield
    logger.info("research_agent_shutdown")


app = FastAPI(
    title="Research Agent API",
    description="Production-grade agentic research and information-gathering platform",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "research-agent"}


@app.get("/metrics")
async def metrics_endpoint():
    return PlainTextResponse(generate_latest(REGISTRY))


@app.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    with metrics.research_run_duration_seconds.time():
        graph = build_graph()
        initial_state = ResearchState(
            question=request.question,
            max_results_per_source=request.max_results_per_source,
            include_sources=request.include_sources,
            time_window_days=request.time_window_days,
        )

        try:
            result = await graph.ainvoke(
                initial_state,
                {"configurable": {"thread_id": "api_run"}},
            )
            metrics.research_runs_total.labels(status=result.get("status", "unknown")).inc()
        except Exception as e:
            logger.error("research_run_failed", error=str(e))
            metrics.research_runs_total.labels(status="failed").inc()
            return ResearchResponse(
                run_id="error",
                status="failed",
                warnings=[f"Research run failed: {e}"],
            )

    return ResearchResponse(
        run_id=result.get("run_id", "unknown"),
        status=result.get("status", "completed"),
        report_markdown=result.get("report_markdown", ""),
        evidence_count=len(result.get("extracted_evidence", [])),
        warnings=result.get("warnings", []),
    )


@app.get("/research/{run_id}")
async def get_run(run_id: str):
    repo = JSONLRepository()
    run = await repo.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/research/{run_id}/evidence")
async def get_run_evidence(run_id: str):
    repo = JSONLRepository()
    run = await repo.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"run_id": run_id, "evidence_count": run.evidence_count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("research_agent.main:app", host="0.0.0.0", port=8000, reload=True)

from __future__ import annotations

from typing import Any

import pytest
from pydantic import BaseModel


@pytest.fixture(autouse=True)
def fail_llm_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make llm_call fail instantly so fallback code paths run immediately.

    Without this, each LLM call retries multiple times with 30s timeouts,
    making integration tests painfully slow when no LLM is reachable.
    """

    async def mock_llm_call(
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel] | None = None,
        max_retries: int = 3,
    ) -> Any:
        msg = "LLM not available in test mode — using fallback"
        raise RuntimeError(msg)

    # Patch every module that does `from research_agent.llm.client import llm_call`,
    # since those create local references at import time that monkeypatch on
    # the source module cannot reach.
    # Patch each importing module so the local reference to llm_call
    # (created via `from ... import llm_call` at module load time)
    # is replaced with the fast-failing mock.
    for module_path in [
        "research_agent.extraction.extractor.llm_call",
        "research_agent.planning.query_planner.llm_call",
        "research_agent.analysis.analyser.llm_call",
    ]:
        monkeypatch.setattr(module_path, mock_llm_call)

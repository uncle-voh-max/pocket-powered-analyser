from __future__ import annotations

from typing import Annotated, Sequence

from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    messages: Annotated[Sequence[dict], add_messages] = Field(default_factory=list)
    is_last_step: IsLastStep = False
    structured_output: dict | None = None
    iteration_count: int = 0

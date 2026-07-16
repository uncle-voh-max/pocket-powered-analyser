from __future__ import annotations

from pydantic import BaseModel, Field

from research_agent.llm.client import llm_call
from research_agent.planning.prompts import QUERY_PLANNER_SYSTEM, QUERY_PLANNER_USER


class SearchPlan(BaseModel):
    news: list[str] = Field(default_factory=list)
    web: list[str] = Field(default_factory=list)
    social: list[str] = Field(default_factory=list)
    reddit: list[str] = Field(default_factory=list)
    wikipedia: list[str] = Field(default_factory=list)


class QueryPlan(BaseModel):
    original_question: str
    research_objective: str
    time_sensitivity: str = "evergreen"
    constraints: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    search_plan: SearchPlan = Field(default_factory=SearchPlan)
    success_criteria: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


async def plan_queries(question: str) -> QueryPlan:
    response = await llm_call(
        system_prompt=QUERY_PLANNER_SYSTEM,
        user_prompt=QUERY_PLANNER_USER.format(question=question),
        response_model=QueryPlan,
        max_retries=2,
    )
    response.original_question = question
    return response

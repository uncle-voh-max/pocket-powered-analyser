from __future__ import annotations

from research_agent.planning.query_planner import QueryPlan, SearchPlan


def test_query_plan_defaults() -> None:
    plan = QueryPlan(original_question="Test", research_objective="Test objective")
    assert plan.original_question == "Test"
    assert plan.research_objective == "Test objective"
    assert plan.time_sensitivity == "evergreen"
    assert plan.constraints == []
    assert plan.entities == []
    assert plan.search_plan.news == []
    assert plan.search_plan.web == []
    assert plan.search_plan.social == []
    assert plan.search_plan.reddit == []
    assert plan.search_plan.wikipedia == []
    assert plan.success_criteria == []
    assert plan.risks == []


def test_search_plan_defaults() -> None:
    sp = SearchPlan()
    assert sp.news == []
    assert sp.web == []
    assert sp.social == []
    assert sp.reddit == []
    assert sp.wikipedia == []


def test_query_plan_with_search_plan() -> None:
    sp = SearchPlan(news=["ai news"], web=["ai research"])
    plan = QueryPlan(
        original_question="AI trends",
        research_objective="Analyse AI trends",
        search_plan=sp,
        entities=["AI", "ML"],
    )
    assert len(plan.search_plan.news) == 1
    assert len(plan.search_plan.web) == 1
    assert "AI" in plan.entities


def test_query_plan_model_dump() -> None:
    plan = QueryPlan(
        original_question="Test?",
        research_objective="Objective",
    )
    data = plan.model_dump()
    assert data["original_question"] == "Test?"
    assert data["research_objective"] == "Objective"
    assert "search_plan" in data
    assert "entities" in data

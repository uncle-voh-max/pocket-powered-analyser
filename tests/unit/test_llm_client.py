from __future__ import annotations

from unittest.mock import patch

import pytest

from research_agent.config import settings
from research_agent.llm.client import _get_model, llm_call
from research_agent.planning.query_planner import QueryPlan


def test_default_provider_is_openai() -> None:
    assert settings.llm_provider == "openai"


def test_effective_model_openai() -> None:
    with patch.object(settings, "llm_provider", "openai"):
        with patch.object(settings, "llm_model", "gpt-4o-mini"):
            assert settings.effective_llm_model == "gpt-4o-mini"


def test_effective_model_ollama() -> None:
    with patch.object(settings, "llm_provider", "ollama"):
        with patch.object(settings, "ollama_model", "llama3.2"):
            assert settings.effective_llm_model == "llama3.2"


def test_get_model_openai() -> None:
    with patch.object(settings, "llm_provider", "openai"):
        with patch.object(settings, "llm_model", "gpt-4o-mini"):
            with patch("research_agent.llm.client.init_chat_model") as mock_init:
                mock_init.return_value = "mock_model"
                model = _get_model()
                assert model == "mock_model"
                mock_init.assert_called_once_with(
                    model="gpt-4o-mini",
                    model_provider="openai",
                    temperature=settings.llm_temperature,
                )


def test_get_model_ollama() -> None:
    with patch.object(settings, "llm_provider", "ollama"):
        with patch.object(settings, "ollama_model", "llama3.2"):
            with patch.object(settings, "ollama_base_url", "http://localhost:11434"):
                model = _get_model()
                assert "ollama" in type(model).__module__.lower()


@pytest.mark.asyncio
async def test_llm_call_fallback_structured_ollama() -> None:
    """Ollama doesn't support native structured output; should fall back to JSON parsing."""
    with patch.object(settings, "llm_provider", "ollama"):
        with patch.object(settings, "ollama_model", "llama3.2"):
            with patch(
                "research_agent.llm.client._get_model",
                autospec=True,
            ) as mock_get_model:
                mock_instance = mock_get_model.return_value

                async def fake_ainvoke(messages):
                    class FakeResponse:
                        content = (
                            '{"original_question": "test", '
                            '"research_objective": "test objective", '
                            '"time_sensitivity": "evergreen"}'
                        )
                    return FakeResponse()

                mock_instance.ainvoke = fake_ainvoke

                result = await llm_call(
                    system_prompt="test",
                    user_prompt="test",
                    response_model=QueryPlan,
                    max_retries=1,
                )
                assert isinstance(result, QueryPlan)
                assert result.original_question == "test"
                assert result.research_objective == "test objective"

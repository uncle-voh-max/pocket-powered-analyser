from __future__ import annotations

from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from research_agent.config import settings
from research_agent.llm.structured_output import safe_parse
from research_agent.logging import logger


_SUPPORTS_NATIVE_STRUCTURED = {"openai", "anthropic", "google-genai"}


def _get_model() -> BaseChatModel:
    kwargs: dict[str, Any] = {
        "model": settings.effective_llm_model,
        "temperature": settings.llm_temperature,
    }

    if settings.llm_provider == "ollama":
        kwargs["model_provider"] = "ollama"
        kwargs["base_url"] = settings.ollama_base_url
    else:
        kwargs["model_provider"] = settings.llm_provider

    return init_chat_model(**kwargs)


async def llm_call(
    system_prompt: str,
    user_prompt: str,
    response_model: type[BaseModel] | None = None,
    max_retries: int = 3,
) -> Any:
    model = _get_model()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    # Use native structured output only for providers that support it
    supports_structured = settings.llm_provider in _SUPPORTS_NATIVE_STRUCTURED
    if response_model is not None and supports_structured:
        model = model.with_structured_output(response_model)

    for attempt in range(max_retries):
        try:
            response = await model.ainvoke(messages)

            # Native structured output already returns the model instance
            if response_model is not None and supports_structured:
                return response

            content = response.content if hasattr(response, "content") else str(response)

            # Fallback: prompt-based structured parsing (Ollama / unsupported providers)
            if response_model is not None and not supports_structured:
                parsed = safe_parse(content, response_model)
                if parsed is not None:
                    return parsed
                logger.warning(
                    "llm_parse_retry",
                    attempt=attempt + 1,
                    model=response_model.__name__,
                    provider=settings.llm_provider,
                )
                continue

            return content
        except Exception as e:
            logger.error(
                "llm_call_failed",
                attempt=attempt + 1,
                error=str(e),
                provider=settings.llm_provider,
            )
            if attempt == max_retries - 1:
                raise

    msg = "LLM call failed after max retries"
    raise RuntimeError(msg)

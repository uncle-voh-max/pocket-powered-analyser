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


def _get_model() -> BaseChatModel:
    return init_chat_model(
        settings.llm_model,
        model_provider=settings.llm_provider,
        temperature=settings.llm_temperature,
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
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

    if response_model is not None:
        model = model.with_structured_output(response_model)

    for attempt in range(max_retries):
        try:
            response = await model.ainvoke(messages)

            if response_model is not None:
                return response

            content = response.content if hasattr(response, "content") else str(response)
            if response_model is not None:
                parsed = safe_parse(content, response_model)
                if parsed is not None:
                    return parsed
                logger.warning(
                    "llm_parse_retry",
                    attempt=attempt + 1,
                    model=response_model.__name__,
                )
                continue
            return content
        except Exception as e:
            logger.error("llm_call_failed", attempt=attempt + 1, error=str(e))
            if attempt == max_retries - 1:
                raise

    msg = "LLM call failed after max retries"
    raise RuntimeError(msg)

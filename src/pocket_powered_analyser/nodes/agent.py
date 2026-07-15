from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from pocket_powered_analyser.state.schema import AgentState

SYSTEM_PROMPT = """You are a senior analysis agent. Your purpose is to analyse data,
reason step by step, and produce structured outputs. Always think carefully before
responding and use the tools at your disposal when needed."""


def _load_model() -> BaseChatModel:
    return init_chat_model("gpt-4o-mini", model_provider="openai")


async def call_agent(
    state: AgentState,
    config: RunnableConfig | None = None,
) -> dict:
    model = _load_model().bind_tools([])
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state.messages]
    response = await model.ainvoke(messages, config)
    return {"messages": [response], "iteration_count": state.iteration_count + 1}


def should_continue(state: AgentState) -> str:
    last = state.messages[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "respond"

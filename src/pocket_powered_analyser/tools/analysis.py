from __future__ import annotations

from langchain_core.tools import tool


@tool
async def summarise_text(text: str, max_length: int = 200) -> str:
    """Summarise the provided text to a maximum number of characters."""
    return text[:max_length] + ("..." if len(text) > max_length else "")


@tool
async def extract_entities(text: str) -> dict[str, list[str]]:
    """Extract named entities from text (placeholder — logic TBD)."""
    return {"people": [], "organisations": [], "locations": []}


tools = [summarise_text, extract_entities]

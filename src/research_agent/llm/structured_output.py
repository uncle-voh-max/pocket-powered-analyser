from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel

from research_agent.logging import logger


def _strip_json_comments(text: str) -> str:
    """Strip JavaScript-style comments (// and /* */) from JSON text."""
    # Strip block comments /* ... */ first
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    # Strip line comments // ... but not inside strings
    result: list[str] = []
    in_string = False
    escape = False
    i = 0
    while i < len(text):
        ch = text[i]
        if escape:
            escape = False
            result.append(ch)
            i += 1
        elif ch == "\\" and in_string:
            escape = True
            result.append(ch)
            i += 1
        elif ch == '"' and not escape:
            in_string = not in_string
            result.append(ch)
            i += 1
        elif not in_string and ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            # Skip to end of line
            i += 2
            while i < len(text) and text[i] != "\n":
                i += 1
        else:
            result.append(ch)
            i += 1
    return "".join(result)


def extract_json(text: str) -> dict[str, Any] | None:
    """Extract JSON from LLM response, handling markdown fences and stray text."""
    # Try ```json ... ``` first
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()

    # Try finding a top-level object
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        text = m.group(0)

    # Strip JS-style comments that some LLMs insert
    text = _strip_json_comments(text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("json_parse_failed", text_preview=text[:200])
        return None


def validate_against_model(
    data: dict[str, Any] | None,
    model_class: type[BaseModel],
) -> BaseModel | None:
    if data is None:
        return None
    try:
        return model_class.model_validate(data)
    except Exception:
        logger.error("model_validation_failed", model=model_class.__name__)
        return None


def safe_parse(text: str, model_class: type[BaseModel]) -> BaseModel | None:
    data = extract_json(text)
    return validate_against_model(data, model_class)

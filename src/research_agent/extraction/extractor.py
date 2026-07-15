from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from research_agent.adapters.base import RawDocument
from research_agent.extraction.chunking import chunk_text
from research_agent.extraction.prompts import EXTRACT_SYSTEM_PROMPT, EXTRACT_USER_PROMPT
from research_agent.llm.client import llm_call


class Claim(BaseModel):
    claim: str
    evidence_text: str = ""
    confidence: float = 0.0
    source_reliability: float = 0.0
    requires_verification: bool = True


class ExtractedEvidence(BaseModel):
    source_type: str = "unknown"
    title: str = ""
    url: str = ""
    publisher_or_platform: str = ""
    published_at: str = ""
    retrieved_at: str = ""
    author: str = ""
    summary: str = ""
    key_points: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    quotes: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    sentiment: str = "unknown"
    limitations: list[str] = Field(default_factory=list)


async def extract_evidence(
    document: RawDocument,
    source_type: str,
) -> ExtractedEvidence:
    text = document.text or ""
    chunks = chunk_text(text)
    first_chunk = chunks[0]

    try:
        result = await llm_call(
            system_prompt=EXTRACT_SYSTEM_PROMPT,
            user_prompt=EXTRACT_USER_PROMPT.format(
                source_type=source_type,
                title=document.title,
                url=document.url,
                publisher=document.title.split(" - ")[-1] if document.title else "",
                author="",
                published="",
                retrieved=datetime.now(timezone.utc).isoformat(),
                document_text=first_chunk[:6000],
            ),
            response_model=ExtractedEvidence,
            max_retries=2,
        )
    except Exception:
        result = ExtractedEvidence(
            source_type=source_type,
            title=document.title,
            url=document.url,
            summary=text[:500] if text else "No extractable content.",
        )

    result.source_type = source_type
    result.title = document.title or result.title
    result.url = document.effective_url or document.url or result.url
    return result

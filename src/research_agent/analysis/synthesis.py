from __future__ import annotations

from pydantic import BaseModel, Field


class SynthesisResult(BaseModel):
    major_themes: list[str] = Field(default_factory=list)
    repeated_claims: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    well_supported: list[str] = Field(default_factory=list)
    weakly_supported: list[str] = Field(default_factory=list)
    requires_more_research: list[str] = Field(default_factory=list)
    missing_sources: list[str] = Field(default_factory=list)
    overall_confidence: float = 0.0
    summary: str = ""

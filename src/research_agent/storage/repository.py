from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


class ResearchRunRecord:
    def __init__(
        self,
        run_id: str,
        question: str,
        status: str = "pending",
        created_at: datetime | None = None,
        report_markdown: str = "",
        evidence_count: int = 0,
        warnings: list[str] | None = None,
    ):
        self.run_id = run_id
        self.question = question
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.report_markdown = report_markdown
        self.evidence_count = evidence_count
        self.warnings = warnings or []


class Repository(ABC):
    @abstractmethod
    async def save_run(self, run: ResearchRunRecord) -> None: ...

    @abstractmethod
    async def get_run(self, run_id: str) -> ResearchRunRecord | None: ...

    @abstractmethod
    async def update_run(
        self,
        run_id: str,
        status: str | None = None,
        report_markdown: str | None = None,
        evidence_count: int | None = None,
        warnings: list[str] | None = None,
    ) -> None: ...

    @abstractmethod
    async def list_runs(self, limit: int = 20) -> list[ResearchRunRecord]: ...

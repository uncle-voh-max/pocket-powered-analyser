from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_agent.storage.repository import Repository, ResearchRunRecord


class JSONLRepository(Repository):
    def __init__(self, path: str | Path = "data/research_runs.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open() as f:
            return [json.loads(line) for line in f if line.strip()]

    def _write_all(self, records: list[dict[str, Any]]) -> None:
        with self.path.open("w") as f:
            for rec in records:
                f.write(json.dumps(rec, default=str) + "\n")

    async def save_run(self, run: ResearchRunRecord) -> None:
        records = self._read_all()
        records.append({
            "run_id": run.run_id,
            "question": run.question,
            "status": run.status,
            "created_at": run.created_at.isoformat(),
            "report_markdown": run.report_markdown,
            "evidence_count": run.evidence_count,
            "warnings": run.warnings,
        })
        self._write_all(records)

    async def get_run(self, run_id: str) -> ResearchRunRecord | None:
        for rec in self._read_all():
            if rec["run_id"] == run_id:
                return ResearchRunRecord(**rec)
        return None

    async def update_run(
        self,
        run_id: str,
        status: str | None = None,
        report_markdown: str | None = None,
        evidence_count: int | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        records = self._read_all()
        for rec in records:
            if rec["run_id"] == run_id:
                if status is not None:
                    rec["status"] = status
                if report_markdown is not None:
                    rec["report_markdown"] = report_markdown
                if evidence_count is not None:
                    rec["evidence_count"] = evidence_count
                if warnings is not None:
                    rec["warnings"] = warnings
                break
        self._write_all(records)

    async def list_runs(self, limit: int = 20) -> list[ResearchRunRecord]:
        records = self._read_all()
        records.reverse()
        return [ResearchRunRecord(**r) for r in records[:limit]]

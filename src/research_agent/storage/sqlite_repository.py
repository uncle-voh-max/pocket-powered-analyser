from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import aiosqlite

from research_agent.storage.repository import Repository, ResearchRunRecord


class SQLiteRepository(Repository):
    def __init__(self, db_path: str = "data/research.db") -> None:
        self.db_path = db_path

    async def _connect(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS research_runs (
                run_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                report_markdown TEXT DEFAULT '',
                evidence_count INTEGER DEFAULT 0,
                warnings TEXT DEFAULT '[]'
            )
        """)
        await conn.commit()
        return conn

    async def save_run(self, run: ResearchRunRecord) -> None:
        conn = await self._connect()
        try:
            await conn.execute(
                """INSERT INTO research_runs (run_id, question, status, created_at, report_markdown, evidence_count, warnings)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    run.run_id,
                    run.question,
                    run.status,
                    run.created_at.isoformat(),
                    run.report_markdown,
                    run.evidence_count,
                    json.dumps(run.warnings),
                ),
            )
            await conn.commit()
        finally:
            await conn.close()

    async def get_run(self, run_id: str) -> ResearchRunRecord | None:
        conn = await self._connect()
        try:
            cursor = await conn.execute(
                "SELECT * FROM research_runs WHERE run_id = ?",
                (run_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return ResearchRunRecord(
                run_id=row["run_id"],
                question=row["question"],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                report_markdown=row["report_markdown"],
                evidence_count=row["evidence_count"],
                warnings=json.loads(row["warnings"]),
            )
        finally:
            await conn.close()

    async def update_run(
        self,
        run_id: str,
        status: str | None = None,
        report_markdown: str | None = None,
        evidence_count: int | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        conn = await self._connect()
        try:
            updates: list[str] = []
            params: list[Any] = []
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if report_markdown is not None:
                updates.append("report_markdown = ?")
                params.append(report_markdown)
            if evidence_count is not None:
                updates.append("evidence_count = ?")
                params.append(evidence_count)
            if warnings is not None:
                updates.append("warnings = ?")
                params.append(json.dumps(warnings))
            if updates:
                params.append(run_id)
                await conn.execute(
                    f"UPDATE research_runs SET {', '.join(updates)} WHERE run_id = ?",
                    params,
                )
                await conn.commit()
        finally:
            await conn.close()

    async def list_runs(self, limit: int = 20) -> list[ResearchRunRecord]:
        conn = await self._connect()
        try:
            cursor = await conn.execute(
                "SELECT * FROM research_runs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
            return [
                ResearchRunRecord(
                    run_id=row["run_id"],
                    question=row["question"],
                    status=row["status"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    report_markdown=row["report_markdown"],
                    evidence_count=row["evidence_count"],
                    warnings=json.loads(row["warnings"]),
                )
                for row in rows
            ]
        finally:
            await conn.close()

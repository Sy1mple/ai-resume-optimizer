from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

from supabase import Client, create_client

from app.models import HistoryRecord, TaskType


class HistoryStore:
    def __init__(self) -> None:
        self._records: list[HistoryRecord] = []
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.client: Client | None = create_client(url, key) if url and key else None

    async def add(self, task_type: TaskType, content: str, user_id: str | None = None) -> HistoryRecord:
        record = HistoryRecord(
            id=str(uuid4()),
            user_id=user_id,
            task_type=task_type,
            content=content,
            created_at=datetime.now(UTC).isoformat(),
        )

        if self.client:
            data = record.model_dump()
            self.client.table("history").insert(data).execute()
        else:
            self._records.insert(0, record)

        return record

    async def list(self, user_id: str | None = None) -> list[HistoryRecord]:
        if self.client:
            query = self.client.table("history").select("*").order("created_at", desc=True).limit(50)
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.execute()
            return [HistoryRecord(**item) for item in response.data]

        if user_id:
            return [record for record in self._records if record.user_id == user_id][:50]
        return self._records[:50]

    async def delete(self, record_id: str) -> bool:
        if self.client:
            self.client.table("history").delete().eq("id", record_id).execute()
            return True

        before = len(self._records)
        self._records = [record for record in self._records if record.id != record_id]
        return len(self._records) != before

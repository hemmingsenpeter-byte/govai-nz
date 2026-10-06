"""Offline adapters; SQLite append-only API is not tamper-resistant storage."""

import json
import sqlite3
from pathlib import Path

from .core import AuditEvent, ModelResponse, Request


class MockProvider:
    provider_id = "mock"

    def generate(self, request: Request) -> ModelResponse:
        return ModelResponse("Synthetic public-document summary for demonstration only.", "mock/v1")


class UnavailableProvider:
    provider_id = "unavailable-mock"

    def generate(self, request: Request) -> ModelResponse:
        raise RuntimeError("Synthetic provider failure")


class SQLiteAuditStore:
    def __init__(self, path: str | Path) -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS events "
            "(sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT UNIQUE NOT NULL, payload TEXT NOT NULL)"
        )
        self.connection.commit()

    def append(self, event: AuditEvent) -> None:
        payload = json.dumps(event.to_dict(), sort_keys=True)
        with self.connection:
            self.connection.execute("INSERT INTO events (event_id, payload) VALUES (?, ?)", (event.event_id, payload))

    def export(self) -> list[dict]:
        return [json.loads(row[0]) for row in self.connection.execute("SELECT payload FROM events ORDER BY sequence")]

    def orphaned_preflights(self) -> list[dict]:
        """Report unresolved requests; do not infer success or retry execution."""
        events = self.export()
        terminal_ids = {event["request_id"] for event in events
                        if event["phase"] in {"completed", "failed", "stopped"}}
        return [event for event in events
                if event["phase"] == "preflight" and event["request_id"] not in terminal_ids]

    def close(self) -> None:
        self.connection.close()

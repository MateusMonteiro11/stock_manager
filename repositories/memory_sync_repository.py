"""Persistência volátil para desenvolvimento e testes offline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from contracts.inventory_snapshot import InventorySnapshot, Marketplace


@dataclass
class MemorySyncRun:
    run_id: int
    marketplace: Marketplace
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str = "RUNNING"
    record_count: int = 0
    error_message: Optional[str] = None


class InMemorySyncRepository:
    """Repository não persistente; nunca representa dados reais da empresa."""

    def __init__(self) -> None:
        self.runs: Dict[int, MemorySyncRun] = {}
        self.snapshots: List[InventorySnapshot] = []

    def begin_run(self, marketplace: Marketplace, started_at: datetime) -> int:
        run_id = len(self.runs) + 1
        self.runs[run_id] = MemorySyncRun(run_id, marketplace, started_at)
        return run_id

    def save_snapshots(
        self,
        run_id: Any,
        snapshots: Sequence[InventorySnapshot],
    ) -> int:
        if run_id not in self.runs:
            raise ValueError("Execução de sincronização inexistente.")
        batch = list(snapshots)
        self.snapshots.extend(batch)
        return len(batch)

    def finish_run(
        self,
        run_id: Any,
        finished_at: datetime,
        status: str,
        record_count: int,
        error_message: Optional[str] = None,
    ) -> None:
        run = self.runs[run_id]
        run.finished_at = finished_at
        run.status = status
        run.record_count = record_count
        run.error_message = error_message

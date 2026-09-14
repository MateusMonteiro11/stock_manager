"""Orquestra a sincronização read-only de inventário."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Iterable, List, Optional, Sequence, Set

from contracts.inventory_snapshot import InventorySnapshot, Marketplace
from integrations.base.marketplace_adapter import (
    IntegrationNotConfiguredError,
    IntegrationUnavailableError,
    MarketplaceAdapter,
)
from repositories.interfaces import SyncRepository


class SyncRunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class SyncStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


@dataclass(frozen=True)
class MarketplaceSyncResult:
    marketplace: Marketplace
    status: SyncRunStatus
    record_count: int
    run_id: Any = None
    error_message: Optional[str] = None


@dataclass(frozen=True)
class SyncResult:
    status: SyncStatus
    started_at: datetime
    finished_at: datetime
    marketplaces: Sequence[MarketplaceSyncResult]

    @property
    def record_count(self) -> int:
        return sum(result.record_count for result in self.marketplaces)


def _safe_error_message(error: Exception) -> str:
    """Retorna informação útil sem copiar mensagens que podem conter tokens."""
    if isinstance(error, IntegrationNotConfiguredError):
        return "Credenciais da integração não configuradas."
    if isinstance(error, IntegrationUnavailableError):
        return "Integração real indisponível enquanto aguarda autorização."
    return f"Sincronização não concluída ({type(error).__name__})."


class SyncService:
    def __init__(
        self,
        adapters: Iterable[MarketplaceAdapter],
        repository: SyncRepository,
        clock: Callable[[], datetime] = None,
    ) -> None:
        self._adapters = list(adapters)
        self._repository = repository
        self._clock = clock or (lambda: datetime.now(timezone.utc))

        for adapter in self._adapters:
            Marketplace.from_value(adapter.marketplace)

    def synchronize(
        self,
        enabled_marketplaces: Optional[Iterable[Marketplace]] = None,
    ) -> SyncResult:
        started_at = self._clock()
        enabled = self._normalize_enabled(enabled_marketplaces)
        results: List[MarketplaceSyncResult] = []

        for adapter in self._adapters:
            marketplace = Marketplace.from_value(adapter.marketplace)
            if enabled is not None and marketplace not in enabled:
                continue
            results.append(self._synchronize_adapter(adapter, marketplace))

        finished_at = self._clock()
        return SyncResult(
            status=self._overall_status(results),
            started_at=started_at,
            finished_at=finished_at,
            marketplaces=tuple(results),
        )

    def _synchronize_adapter(
        self,
        adapter: MarketplaceAdapter,
        marketplace: Marketplace,
    ) -> MarketplaceSyncResult:
        run_id = None
        record_count = 0
        try:
            run_id = self._repository.begin_run(marketplace, self._clock())
            adapter.authenticate()
            snapshots = list(adapter.get_inventory())
            self._validate_snapshots(snapshots, marketplace)
            record_count = self._repository.save_snapshots(run_id, snapshots)
            self._repository.finish_run(
                run_id,
                self._clock(),
                SyncRunStatus.SUCCESS.value,
                record_count,
            )
            return MarketplaceSyncResult(
                marketplace=marketplace,
                status=SyncRunStatus.SUCCESS,
                record_count=record_count,
                run_id=run_id,
            )
        except Exception as error:
            error_message = _safe_error_message(error)
            if run_id is not None:
                try:
                    self._repository.finish_run(
                        run_id,
                        self._clock(),
                        SyncRunStatus.FAILED.value,
                        0,
                        error_message,
                    )
                except Exception:
                    # A falha de persistência não deve impedir os demais adapters.
                    pass
            return MarketplaceSyncResult(
                marketplace=marketplace,
                status=SyncRunStatus.FAILED,
                record_count=0,
                run_id=run_id,
                error_message=error_message,
            )

    @staticmethod
    def _validate_snapshots(
        snapshots: Sequence[InventorySnapshot],
        marketplace: Marketplace,
    ) -> None:
        for snapshot in snapshots:
            if not isinstance(snapshot, InventorySnapshot):
                raise ValueError("Adapter retornou um registro fora do contrato interno.")
            if snapshot.marketplace != marketplace:
                raise ValueError("Adapter retornou snapshot de outro marketplace.")

    @staticmethod
    def _normalize_enabled(
        enabled_marketplaces: Optional[Iterable[Marketplace]],
    ) -> Optional[Set[Marketplace]]:
        if enabled_marketplaces is None:
            return None
        return {Marketplace.from_value(value) for value in enabled_marketplaces}

    @staticmethod
    def _overall_status(results: Sequence[MarketplaceSyncResult]) -> SyncStatus:
        successes = sum(result.status == SyncRunStatus.SUCCESS for result in results)
        if successes == len(results) and results:
            return SyncStatus.SUCCESS
        if successes:
            return SyncStatus.PARTIAL
        return SyncStatus.FAILED

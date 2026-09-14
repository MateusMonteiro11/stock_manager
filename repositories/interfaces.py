"""Interfaces de persistência consumidas pela camada de serviços."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Optional, Protocol, Sequence, Tuple

from contracts.inventory_snapshot import InventorySnapshot, Marketplace

ProductRow = Tuple[int, str, str, Optional[str], int]
AuditRow = Tuple[int, str, int, str, str]
MarketplaceAuditRow = Tuple[str, int]


class ProductRepository(Protocol):
    def create(self, name: str, sku: str, category: str) -> Any: ...

    def list_all(self) -> Sequence[ProductRow]: ...

    def find_by_id(self, product_id: int) -> Optional[ProductRow]: ...

    def update_stock(self, product_id: int, quantity: int) -> Any: ...

    def remove(self, product_id: int) -> Any: ...

    def sku_exists(self, sku: str) -> bool: ...


class AuditRepository(Protocol):
    def create(
        self,
        consolidated_stock: int,
        status: str,
        audited_at: str,
        product_id: int,
    ) -> Optional[int]: ...

    def save_marketplace_stock(
        self,
        found_stock: int,
        audit_id: int,
        marketplace: Marketplace,
    ) -> Any: ...

    def list_all(self) -> Sequence[AuditRow]: ...


class ReportRepository(Protocol):
    def list_all(self) -> Sequence[AuditRow]: ...

    def list_marketplaces(self, audit_id: int) -> Sequence[MarketplaceAuditRow]: ...


class SyncRepository(Protocol):
    """Boundary da futura persistência MySQL da sincronização.

    ``save_snapshots`` deve persistir o lote atomicamente: ou todos os snapshots
    da execução são gravados, ou nenhum deles é.
    """

    def begin_run(self, marketplace: Marketplace, started_at: datetime) -> Any: ...

    def save_snapshots(
        self,
        run_id: Any,
        snapshots: Sequence[InventorySnapshot],
    ) -> int: ...

    def finish_run(
        self,
        run_id: Any,
        finished_at: datetime,
        status: str,
        record_count: int,
        error_message: Optional[str] = None,
    ) -> Any: ...

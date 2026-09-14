"""Converte payloads do Mercado Livre no contrato interno do MyStock."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Mapping, Optional

from contracts.inventory_snapshot import (
    InventorySnapshot,
    InventoryStatus,
    Marketplace,
)


def _quantity(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("Quantidade inválida no payload do Mercado Livre.")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as exc:
            raise ValueError("Quantidade inválida no payload do Mercado Livre.") from exc
    raise ValueError("Quantidade inválida no payload do Mercado Livre.")


def _status(value: object) -> InventoryStatus:
    normalized = str(value or "").strip().lower()
    return {
        "active": InventoryStatus.ACTIVE,
        "paused": InventoryStatus.PAUSED,
        "closed": InventoryStatus.CLOSED,
        "inactive": InventoryStatus.INACTIVE,
        "under_review": InventoryStatus.INACTIVE,
    }.get(normalized, InventoryStatus.UNKNOWN)


class MercadoLivreInventoryNormalizer:
    """Normalizador isolado do restante das regras de negócio."""

    def normalize(
        self,
        payload: Mapping[str, Any],
        captured_at: Optional[datetime] = None,
    ) -> List[InventorySnapshot]:
        if not isinstance(payload, Mapping):
            raise ValueError("Payload do Mercado Livre inválido.")

        account_id = payload.get("seller_id")
        timestamp = payload.get("captured_at") or captured_at or datetime.now(timezone.utc)
        items = payload.get("results")
        if not isinstance(items, list):
            raise ValueError("Payload do Mercado Livre sem lista de itens.")

        snapshots: List[InventorySnapshot] = []
        for item in items:
            if not isinstance(item, Mapping):
                raise ValueError("Item inválido no payload do Mercado Livre.")
            variations = item.get("variations") or []
            if variations:
                for variation in variations:
                    if not isinstance(variation, Mapping):
                        raise ValueError("Variação inválida no payload do Mercado Livre.")
                    snapshots.append(
                        self._snapshot(account_id, item, variation, timestamp)
                    )
            else:
                snapshots.append(self._snapshot(account_id, item, None, timestamp))
        return snapshots

    @staticmethod
    def _snapshot(
        account_id: object,
        item: Mapping[str, Any],
        variation: Optional[Mapping[str, Any]],
        captured_at: object,
    ) -> InventorySnapshot:
        source = variation or item
        return InventorySnapshot(
            marketplace=Marketplace.MERCADO_LIVRE,
            account_id=account_id,
            external_item_id=item.get("id"),
            external_variant_id=variation.get("id") if variation else None,
            sku=source.get("seller_custom_field") or source.get("sku"),
            product_name=item.get("title"),
            quantity=_quantity(source.get("available_quantity")),
            status=_status(item.get("status")),
            location_id=source.get("location_id"),
            captured_at=captured_at,
        )

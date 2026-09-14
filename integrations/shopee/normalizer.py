"""Converte payloads da Shopee no contrato interno do MyStock."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Mapping, Optional, Sequence

from contracts.inventory_snapshot import (
    InventorySnapshot,
    InventoryStatus,
    Marketplace,
)


def _quantity(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("Quantidade inválida no payload da Shopee.")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as exc:
            raise ValueError("Quantidade inválida no payload da Shopee.") from exc
    raise ValueError("Quantidade inválida no payload da Shopee.")


def _status(value: object) -> InventoryStatus:
    normalized = str(value or "").strip().upper()
    return {
        "NORMAL": InventoryStatus.ACTIVE,
        "LIVE": InventoryStatus.ACTIVE,
        "UNLIST": InventoryStatus.PAUSED,
        "INACTIVE": InventoryStatus.INACTIVE,
        "BANNED": InventoryStatus.CLOSED,
        "DELETED": InventoryStatus.CLOSED,
    }.get(normalized, InventoryStatus.UNKNOWN)


def _stock_entries(source: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    stock_info = source.get("stock_info_v2") or {}
    if isinstance(stock_info, Mapping):
        seller_stock = stock_info.get("seller_stock") or []
        if isinstance(seller_stock, list) and seller_stock:
            return seller_stock
    return [{"stock": source.get("stock"), "location_id": source.get("location_id")}]


class ShopeeInventoryNormalizer:
    """Normalizador isolado do restante das regras de negócio."""

    def normalize(
        self,
        payload: Mapping[str, Any],
        captured_at: Optional[datetime] = None,
    ) -> List[InventorySnapshot]:
        if not isinstance(payload, Mapping):
            raise ValueError("Payload da Shopee inválido.")

        account_id = payload.get("shop_id")
        timestamp = payload.get("captured_at") or captured_at or datetime.now(timezone.utc)
        items = payload.get("item_list")
        if not isinstance(items, list):
            raise ValueError("Payload da Shopee sem lista de itens.")

        snapshots: List[InventorySnapshot] = []
        for item in items:
            if not isinstance(item, Mapping):
                raise ValueError("Item inválido no payload da Shopee.")
            models = item.get("model") or []
            if models:
                for model in models:
                    snapshots.extend(self._snapshots(account_id, item, model, timestamp))
            else:
                snapshots.extend(self._snapshots(account_id, item, None, timestamp))
        return snapshots

    @staticmethod
    def _snapshots(
        account_id: object,
        item: Mapping[str, Any],
        model: Optional[Mapping[str, Any]],
        captured_at: object,
    ) -> List[InventorySnapshot]:
        if model is not None and not isinstance(model, Mapping):
            raise ValueError("Variação inválida no payload da Shopee.")
        source = model or item
        snapshots = []
        for stock in _stock_entries(source):
            if not isinstance(stock, Mapping):
                raise ValueError("Estoque inválido no payload da Shopee.")
            snapshots.append(
                InventorySnapshot(
                    marketplace=Marketplace.SHOPEE,
                    account_id=account_id,
                    external_item_id=item.get("item_id"),
                    external_variant_id=model.get("model_id") if model else None,
                    sku=(source.get("model_sku") if model else source.get("item_sku")),
                    product_name=item.get("item_name"),
                    quantity=_quantity(stock.get("stock")),
                    status=_status(item.get("item_status")),
                    location_id=stock.get("location_id"),
                    captured_at=captured_at,
                )
            )
        return snapshots

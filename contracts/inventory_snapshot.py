"""Contrato interno de inventário do MyStock.

Os objetos deste módulo são dados normalizados da aplicação. Eles não representam
nem expõem o JSON bruto retornado por qualquer marketplace.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class Marketplace(str, Enum):
    SHOPEE = "shopee"
    MERCADO_LIVRE = "mercado_livre"

    @property
    def display_name(self) -> str:
        return {
            Marketplace.SHOPEE: "Shopee",
            Marketplace.MERCADO_LIVRE: "Mercado Livre",
        }[self]

    @classmethod
    def from_value(cls, value: object) -> "Marketplace":
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValueError("Marketplace inválido.")

        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ValueError("Marketplace inválido.") from exc


class InventoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_value(cls, value: object) -> "InventoryStatus":
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValueError("Status de inventário inválido.")
        try:
            return cls(value.strip().upper())
        except ValueError as exc:
            raise ValueError("Status de inventário inválido.") from exc


def parse_timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        timestamp = value.strip()
        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(timestamp)
        except ValueError as exc:
            raise ValueError("captured_at deve ser um timestamp ISO 8601 válido.") from exc
    else:
        raise ValueError("captured_at deve ser um timestamp válido.")

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("captured_at deve conter fuso horário.")
    return parsed.astimezone(timezone.utc)


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, (str, int)):
        raise ValueError(f"{field_name} é obrigatório.")
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} é obrigatório.")
    return normalized


def _optional_text(value: object) -> Optional[str]:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


@dataclass(frozen=True)
class InventorySnapshot:
    marketplace: Marketplace
    account_id: str
    external_item_id: str
    external_variant_id: Optional[str]
    sku: Optional[str]
    product_name: str
    quantity: int
    status: InventoryStatus
    location_id: Optional[str]
    captured_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "marketplace", Marketplace.from_value(self.marketplace))
        object.__setattr__(self, "status", InventoryStatus.from_value(self.status))
        object.__setattr__(self, "account_id", _required_text(self.account_id, "account_id"))
        object.__setattr__(
            self,
            "external_item_id",
            _required_text(self.external_item_id, "external_item_id"),
        )
        object.__setattr__(self, "product_name", _required_text(self.product_name, "product_name"))
        object.__setattr__(self, "external_variant_id", _optional_text(self.external_variant_id))
        object.__setattr__(self, "sku", _optional_text(self.sku))
        object.__setattr__(self, "location_id", _optional_text(self.location_id))
        object.__setattr__(self, "captured_at", parse_timestamp(self.captured_at))

        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise ValueError("quantity deve ser um número inteiro.")
        if self.quantity < 0:
            raise ValueError("quantity não pode ser negativa.")

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["marketplace"] = self.marketplace.value
        data["status"] = self.status.value
        data["captured_at"] = self.captured_at.isoformat().replace("+00:00", "Z")
        return data

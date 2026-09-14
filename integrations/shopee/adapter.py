"""Adapter read-only da Shopee."""

from typing import Any, Mapping, Sequence

from contracts.inventory_snapshot import InventorySnapshot, Marketplace
from integrations.base.marketplace_adapter import MarketplaceAdapter
from integrations.shopee.client import ShopeeClient
from integrations.shopee.normalizer import ShopeeInventoryNormalizer


class ShopeeAdapter(MarketplaceAdapter):
    def __init__(self, client=None, normalizer=None) -> None:
        self._client = client or ShopeeClient()
        self._normalizer = normalizer or ShopeeInventoryNormalizer()

    @property
    def marketplace(self) -> Marketplace:
        return Marketplace.SHOPEE

    def authenticate(self) -> None:
        self._client.authenticate()

    def get_account(self) -> Mapping[str, Any]:
        return self._client.get_account()

    def get_inventory(self) -> Sequence[InventorySnapshot]:
        return self._normalizer.normalize(self._client.get_inventory_payload())

    def health_check(self) -> bool:
        return self._client.health_check()

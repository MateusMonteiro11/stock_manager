"""Adapter read-only do Mercado Livre."""

from typing import Any, Mapping, Sequence

from contracts.inventory_snapshot import InventorySnapshot, Marketplace
from integrations.base.marketplace_adapter import MarketplaceAdapter
from integrations.mercadolivre.client import MercadoLivreClient
from integrations.mercadolivre.normalizer import MercadoLivreInventoryNormalizer


class MercadoLivreAdapter(MarketplaceAdapter):
    def __init__(self, client=None, normalizer=None) -> None:
        self._client = client or MercadoLivreClient()
        self._normalizer = normalizer or MercadoLivreInventoryNormalizer()

    @property
    def marketplace(self) -> Marketplace:
        return Marketplace.MERCADO_LIVRE

    def authenticate(self) -> None:
        self._client.authenticate()

    def get_account(self) -> Mapping[str, Any]:
        return self._client.get_account()

    def get_inventory(self) -> Sequence[InventorySnapshot]:
        return self._normalizer.normalize(self._client.get_inventory_payload())

    def health_check(self) -> bool:
        return self._client.health_check()

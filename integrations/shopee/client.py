"""Placeholder seguro do futuro cliente HTTP oficial da Shopee."""

from typing import Any, Mapping

from integrations.base.marketplace_adapter import (
    IntegrationNotConfiguredError,
    IntegrationUnavailableError,
)
from integrations.shopee.auth import ShopeeAuthConfig


class ShopeeClient:
    """Não realiza rede até que a Mont Casa autorize a integração oficial."""

    def __init__(self, auth: ShopeeAuthConfig = None) -> None:
        self._auth = auth or ShopeeAuthConfig.from_environment()

    def _raise_unavailable(self) -> None:
        if not self._auth.is_configured:
            raise IntegrationNotConfiguredError("Integração Shopee ainda não configurada.")
        raise IntegrationUnavailableError(
            "Integração Shopee aguarda autorização oficial."
        )

    def authenticate(self) -> None:
        self._raise_unavailable()

    def get_account(self) -> Mapping[str, Any]:
        self._raise_unavailable()

    def get_inventory_payload(self) -> Mapping[str, Any]:
        self._raise_unavailable()

    def health_check(self) -> bool:
        self._raise_unavailable()

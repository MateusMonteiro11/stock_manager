"""Placeholder seguro do futuro cliente HTTP oficial do Mercado Livre."""

from typing import Any, Mapping

from integrations.base.marketplace_adapter import (
    IntegrationNotConfiguredError,
    IntegrationUnavailableError,
)
from integrations.mercadolivre.auth import MercadoLivreAuthConfig


class MercadoLivreClient:
    """Não realiza rede até que a Mont Casa autorize a integração oficial."""

    def __init__(self, auth: MercadoLivreAuthConfig = None) -> None:
        self._auth = auth or MercadoLivreAuthConfig.from_environment()

    def _raise_unavailable(self) -> None:
        if not self._auth.is_configured:
            raise IntegrationNotConfiguredError(
                "Integração Mercado Livre ainda não configurada."
            )
        raise IntegrationUnavailableError(
            "Integração Mercado Livre aguarda autorização oficial."
        )

    def authenticate(self) -> None:
        self._raise_unavailable()

    def get_account(self) -> Mapping[str, Any]:
        self._raise_unavailable()

    def get_inventory_payload(self) -> Mapping[str, Any]:
        self._raise_unavailable()

    def health_check(self) -> bool:
        self._raise_unavailable()

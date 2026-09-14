"""Configuração de autenticação do Mercado Livre, sem executar OAuth."""

from dataclasses import dataclass, field
import os
from typing import Optional


def _env(name: str) -> Optional[str]:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


@dataclass(frozen=True)
class MercadoLivreAuthConfig:
    client_id: Optional[str] = field(default=None, repr=False)
    client_secret: Optional[str] = field(default=None, repr=False)
    access_token: Optional[str] = field(default=None, repr=False)
    refresh_token: Optional[str] = field(default=None, repr=False)

    @classmethod
    def from_environment(cls) -> "MercadoLivreAuthConfig":
        return cls(
            client_id=_env("MERCADO_LIVRE_CLIENT_ID"),
            client_secret=_env("MERCADO_LIVRE_CLIENT_SECRET"),
            access_token=_env("MERCADO_LIVRE_ACCESS_TOKEN"),
            refresh_token=_env("MERCADO_LIVRE_REFRESH_TOKEN"),
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.access_token)

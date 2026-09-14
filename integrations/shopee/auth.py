"""Configuração de autenticação da Shopee, sem executar OAuth."""

from dataclasses import dataclass, field
import os
from typing import Optional


def _env(name: str) -> Optional[str]:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


@dataclass(frozen=True)
class ShopeeAuthConfig:
    partner_id: Optional[str] = field(default=None, repr=False)
    partner_key: Optional[str] = field(default=None, repr=False)
    shop_id: Optional[str] = field(default=None, repr=False)
    access_token: Optional[str] = field(default=None, repr=False)
    refresh_token: Optional[str] = field(default=None, repr=False)

    @classmethod
    def from_environment(cls) -> "ShopeeAuthConfig":
        return cls(
            partner_id=_env("SHOPEE_PARTNER_ID"),
            partner_key=_env("SHOPEE_PARTNER_KEY"),
            shop_id=_env("SHOPEE_SHOP_ID"),
            access_token=_env("SHOPEE_ACCESS_TOKEN"),
            refresh_token=_env("SHOPEE_REFRESH_TOKEN"),
        )

    @property
    def is_configured(self) -> bool:
        return bool(
            self.partner_id
            and self.partner_key
            and self.shop_id
            and self.access_token
        )

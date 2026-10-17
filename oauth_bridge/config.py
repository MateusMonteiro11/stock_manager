"""Configuração da ponte pública e do listener de desenvolvimento."""

from dataclasses import dataclass
import ipaddress
import os
from urllib.parse import urlsplit


PUBLIC_CALLBACK_PATH = "/api/mercadolivre/oauth/callback"
NOTIFICATION_PATH = "/api/mercadolivre/notifications"
LOCAL_CALLBACK_PATH = "/oauth/mercadolivre/callback"


def validate_public_url(value: str, expected_path: str) -> str:
    """Exige HTTPS público, sem dados variáveis, credenciais ou loopback."""
    message = "Configure uma URL pública HTTPS com o caminho esperado."
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
        if (
            not value or not value.isascii()
            or any(char.isspace() or ord(char) < 32 for char in value)
            or "\\" in value or "%" in parsed.netloc
            or parsed.scheme != "https" or not host
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment or "?" in value or "#" in value
            or parsed.path != expected_path or port not in (None, 443)
        ):
            raise ValueError(message)
        host = host.rstrip(".").lower()
        if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
            raise ValueError(message)
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            # Também rejeita IPs abreviados como 127.1 e nomes sem domínio.
            if "." not in host or all(c in "0123456789." for c in host):
                raise ValueError(message) from None
            if any(not label or label.startswith("-") or label.endswith("-")
                   or not all(c.isalnum() or c == "-" for c in label)
                   for label in host.split(".")):
                raise ValueError(message)
        else:
            if not address.is_global:
                raise ValueError(message)
    except (ValueError, TypeError):
        raise ValueError(message) from None
    return value


@dataclass(frozen=True)
class LocalCallbackConfig:
    host: str = "127.0.0.1"
    port: int = 8765

    def __post_init__(self):
        if self.host != "127.0.0.1":
            raise ValueError("O listener deve usar exclusivamente 127.0.0.1.")
        if type(self.port) is not int or not 1 <= self.port <= 65535:
            raise ValueError("Porta local inválida.")

    @classmethod
    def from_environment(cls):
        try:
            port = int(os.environ.get("MERCADO_LIVRE_LOCAL_CALLBACK_PORT", "8765"))
        except ValueError:
            raise ValueError("Porta local inválida.") from None
        return cls(
            host=os.environ.get("MERCADO_LIVRE_LOCAL_CALLBACK_HOST", "127.0.0.1"),
            port=port,
        )

    @property
    def url(self):
        return f"http://{self.host}:{self.port}{LOCAL_CALLBACK_PATH}"

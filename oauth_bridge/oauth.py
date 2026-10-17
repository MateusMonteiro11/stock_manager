"""Validação sintática; a validação criptográfica de state pertence ao listener."""

from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlsplit


@dataclass(frozen=True)
class OAuthCallback:
    state: str = field(repr=False)
    code: str = field(default="", repr=False)
    failed: bool = False

    def relay_parameters(self):
        if self.failed:
            # Não refletir error_description/error_uri enviados pelo provedor.
            return {"error": "authorization_failed", "state": self.state}
        return {"code": self.code, "state": self.state}


def parse_callback(target: str) -> OAuthCallback:
    message = "Callback OAuth inválido."
    try:
        if len(target) > 8192:
            raise ValueError(message)
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or parsed.fragment:
            raise ValueError(message)
        query = parse_qs(parsed.query, keep_blank_values=True, max_num_fields=16,
                         encoding="utf-8", errors="strict")

        def single(name, limit):
            values = query.get(name, [])
            if not values:
                return ""
            if len(values) != 1:
                raise ValueError(message)
            value = values[0]
            if (not value or len(value) > limit or not value.isascii()
                    or any(ord(c) < 33 or ord(c) > 126 for c in value)):
                raise ValueError(message)
            return value

        state = single("state", 512)
        code = single("code", 2048)
        error = single("error", 256)
        if not state or bool(code) == bool(error):
            raise ValueError(message)
    except (ValueError, UnicodeError):
        raise ValueError(message) from None
    return OAuthCallback(state=state, code=code, failed=bool(error))

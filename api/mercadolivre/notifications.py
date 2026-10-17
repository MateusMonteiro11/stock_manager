"""ACK e descarte deliberado; sem fila, banco, auditoria ou processamento remoto.

Este webhook satisfaz o endpoint público necessário para recebimento de
notificações, mas a Sprint atual não utiliza notificações como fonte de estado.
O estado autoritativo é obtido posteriormente pelas operações read-only da API.
"""

import json

from oauth_bridge.http import PrivateHandler


MAX_BODY_BYTES = 64 * 1024


class handler(PrivateHandler):
    allowed_method = "POST"

    def do_POST(self):
        if self.headers.get("Transfer-Encoding"):
            self.respond(400, "Corpo inválido.")
            return
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
            self.respond(400, "Tamanho do corpo inválido.")
            return
        # Limita antes de converter inteiros arbitrariamente grandes.
        if len(lengths[0]) > 8 or int(lengths[0]) > MAX_BODY_BYTES:
            self.respond(413, "Corpo excede o limite.")
            return
        if self.headers.get_content_type() != "application/json":
            self.respond(415, "Envie application/json.")
            return
        try:
            payload = json.loads(self.rfile.read(int(lengths[0])))
        except (ValueError, UnicodeError, RecursionError):
            self.respond(400, "Notificação inválida.")
            return
        if (
            not isinstance(payload, dict)
            or not isinstance(payload.get("topic"), str)
            or not payload["topic"].strip()
            or not isinstance(payload.get("resource"), str)
            or not payload["resource"].startswith("/")
            or payload["resource"].startswith("//")
            or type(payload.get("user_id")) not in (str, int)
            or not str(payload["user_id"]).isascii()
            or not str(payload["user_id"]).isdigit()
            or len(str(payload["user_id"])) > 32
            or int(payload["user_id"]) <= 0
        ):
            self.respond(400, "Notificação inválida.")
            return
        # Estrutura não comprova origem. Nada do payload autoriza ações.
        self.respond(200, "OK")

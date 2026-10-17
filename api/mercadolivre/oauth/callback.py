"""Ponte stateless: navegador -> HTTPS -> loopback, sem troca de tokens."""

from urllib.parse import urlencode

from oauth_bridge.config import LocalCallbackConfig
from oauth_bridge.http import PrivateHandler
from oauth_bridge.oauth import parse_callback


class handler(PrivateHandler):
    allowed_method = "GET"

    def do_GET(self):
        try:
            callback = parse_callback(self.path)
        except ValueError:
            self.respond(400, "Callback OAuth inválido.")
            return
        try:
            destination = LocalCallbackConfig.from_environment().url
        except ValueError:
            self.respond(503, "Destino local indisponível.")
            return
        # code/state aparecem somente no Location necessário ao encaminhamento.
        # O servidor não consulta localhost: o navegador faz essa navegação.
        self.respond(302, headers={
            "Location": destination + "?" + urlencode(callback.relay_parameters()),
        })

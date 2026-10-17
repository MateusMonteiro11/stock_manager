"""Prova local de redirect URI: state de uso único e code descartado em memória."""

import argparse
from http.server import HTTPServer
import os
import secrets
import time
from urllib.parse import urlencode, urlsplit
import webbrowser

from oauth_bridge.config import (
    LOCAL_CALLBACK_PATH, NOTIFICATION_PATH, PUBLIC_CALLBACK_PATH,
    LocalCallbackConfig, validate_public_url,
)
from oauth_bridge.http import PrivateHandler
from oauth_bridge.oauth import parse_callback


AUTHORIZATION_URL = "https://auth.mercadolivre.com.br/authorization"


def authorization_url(client_id, redirect_uri, state):
    if not client_id or not client_id.isascii() or not client_id.isdigit():
        raise ValueError("Configure MERCADO_LIVRE_CLIENT_ID com o App ID oficial.")
    validate_public_url(redirect_uri, PUBLIC_CALLBACK_PATH)
    return AUTHORIZATION_URL + "?" + urlencode({
        "response_type": "code", "client_id": client_id,
        "redirect_uri": redirect_uri, "state": state,
    })


class LocalOAuthServer(HTTPServer):
    def __init__(self, config, timeout_seconds=300):
        if config.host != "127.0.0.1":
            raise ValueError("O listener deve usar exclusivamente 127.0.0.1.")
        super().__init__((config.host, config.port), LocalOAuthHandler)
        self.expected_state = secrets.token_urlsafe(32)
        self.deadline = time.monotonic() + timeout_seconds
        self.outcome = None
        self.timeout = 0.5

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(2)
        return connection, address

    def handle_error(self, request, client_address):
        # Tracebacks de handlers nunca devem expor dados de callback.
        pass


class LocalOAuthHandler(PrivateHandler):
    allowed_method = "GET"

    def do_GET(self):
        try:
            if urlsplit(self.path).path != LOCAL_CALLBACK_PATH:
                self.respond(404, "Caminho não encontrado.")
                return
            callback = parse_callback(self.path)
        except ValueError:
            self.respond(400, "Callback OAuth inválido.")
            return
        server = self.server
        if server.outcome is not None or time.monotonic() >= server.deadline:
            self.respond(410, "Tentativa encerrada. Reinicie o listener.")
            return
        if not secrets.compare_digest(callback.state, server.expected_state):
            self.respond(400, "State inválido.")
            return
        server.expected_state = ""
        server.outcome = "denied" if callback.failed else "received"
        # Só o resultado é retido. O authorization code nunca é armazenado.
        self.respond(200, (
            "Autorização não concluída. Nenhum token foi solicitado."
            if callback.failed else
            "State validado e authorization code recebido. Nenhum token foi solicitado."
        ))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-browser", action="store_true",
                        help="Mostra a URL de autorização para abertura manual.")
    parser.add_argument("--port", type=int, help="Porta loopback (padrão: 8765).")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Validade da tentativa em segundos (padrão: 300).")
    args = parser.parse_args(argv)
    try:
        config = LocalCallbackConfig.from_environment()
        if args.port is not None:
            config = LocalCallbackConfig(config.host, args.port)
        if not 1 <= args.timeout <= 1800:
            raise ValueError("Timeout deve estar entre 1 e 1800 segundos.")
        client_id = os.environ.get("MERCADO_LIVRE_CLIENT_ID", "")
        redirect_uri = os.environ.get("MERCADO_LIVRE_REDIRECT_URI", "")
        # Valida antes de abrir a porta ou o navegador.
        authorization_url(client_id, redirect_uri, "validation")
        notification_url = os.environ.get("MERCADO_LIVRE_NOTIFICATION_URL", "")
        if notification_url:
            validate_public_url(notification_url, NOTIFICATION_PATH)
        with LocalOAuthServer(config, args.timeout) as server:
            url = authorization_url(client_id, redirect_uri, server.expected_state)
            print(f"Aguardando callback em {config.url} por até {args.timeout}s.")
            if args.no_browser:
                # Esta URL inicial contém state, mas nunca authorization code.
                print(url)
            elif not webbrowser.open(url):
                print("Não foi possível abrir o navegador. Use --no-browser.")
                return 1
            while server.outcome is None and time.monotonic() < server.deadline:
                server.handle_request()
            if server.outcome == "received":
                print("State validado; authorization code recebido e descartado. Sem tokens.")
                return 0
            if server.outcome == "denied":
                print("Autorização não concluída. Nenhum token foi solicitado.")
                return 1
            print("Tempo esgotado. Inicie uma nova tentativa.")
            return 1
    except ValueError as error:
        print(str(error))  # Mensagens locais fixas, sem valores de configuração.
        return 1
    except OSError:
        print("Não foi possível iniciar o listener ou abrir o navegador.")
        return 1
    except KeyboardInterrupt:
        print("Validação interrompida.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

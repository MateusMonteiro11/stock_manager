"""HTTP mínimo sem logs de URLs, queries ou corpos."""

from http.server import BaseHTTPRequestHandler


class PrivateHandler(BaseHTTPRequestHandler):
    allowed_method = ""

    def log_message(self, format, *args):
        # BaseHTTPRequestHandler normalmente registra a request line com query.
        pass

    def respond(self, status, message="", headers=None):
        body = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.close_connection = True
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_error(self, code, message=None, explain=None):
        # Nunca refletir método, request line ou texto recebido em erros HTTP.
        self.respond(code, "Requisição rejeitada.")

    def method_not_allowed(self):
        self.respond(405, "Método não permitido.", {"Allow": self.allowed_method})

    def __getattr__(self, name):
        if name.startswith("do_"):
            return self.method_not_allowed
        raise AttributeError(name)

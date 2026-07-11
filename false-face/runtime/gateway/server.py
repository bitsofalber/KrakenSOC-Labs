#!/usr/bin/env python3
"""Gateway/portal interno de Northwind (HTTP en claro). El atacante lo suplanta
por ARP. La pagina de admin lleva un session_token (la flag)."""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/session_token.txt")


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


TOKEN = read_token()


class H(BaseHTTPRequestHandler):
    server_version = "NorthwindGW/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == "/health":
            body = b"ok"
        else:
            body = (
                "<html><body><h1>Northwind Internal Gateway</h1>"
                f"<p>session_token: {TOKEN}</p></body></html>"
            ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    print("[gateway] HTTP en claro en 0.0.0.0:80 (suplantable por ARP)", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()


if __name__ == "__main__":
    main()

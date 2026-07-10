#!/usr/bin/env python3
"""
Servidor web malicioso que sirve un ejecutable por HTTP EN CLARO (puerto 80).

Simula un sitio de descargas comprometido/typosquat desde el que un empleado se
baja un "instalador" que en realidad es un binario malicioso. Como la descarga
va por HTTP sin cifrar, el fichero completo viaja legible por la red y puede
reconstruirse del PCAP (Export Objects). El binario lleva un token embebido (la
flag).

MITRE ATT&CK: T1105 (Ingress Tool Transfer), T1189 (Drive-by Compromise).

NOTA DE MANTENEDOR: el token (la flag) va embebido en el binario y se lee de
/seed/payload_token.txt. En el repositorio ese fichero es un DECOY; el token real
se inyecta solo en el build de CI desde un secret (ver README y workflow release).
"""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("HTTP_PORT", "80"))
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/payload_token.txt")
MALWARE_PATH = "/downloads/Invoice_Viewer_Setup.exe"
SERVER_BANNER = "nginx/1.18.0 (compromised)"


def log(msg):
    print(msg, flush=True)


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


def build_malware(token):
    """Construye un PE 'falso' reconocible (cabecera MZ + stub DOS) con la flag."""
    dos_header = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00"
    dos_stub = b"This program cannot be run in DOS mode.\r\r\n$"
    pe_sig = b"PE\x00\x00"  # firma PE (marca que es un ejecutable Windows)
    body = (
        b"\x00" * 32
        + b".text\x00\x00\x00"           # nombre de seccion tipico
        + b"NorthwindInvoiceViewer v2.1\x00"
        + b"payload-token: " + token.encode("utf-8") + b"\x00"
        + b"\x00" * 64
    )
    return dos_header + b"\x40" + b"\x00" * 47 + dos_stub + pe_sig + body


LANDING = (
    "<!doctype html><html><head><meta charset='utf-8'>"
    "<title>Northwind Invoice Portal</title></head><body>"
    "<h1>Northwind Invoice Portal</h1>"
    "<p>Para ver su factura, descargue e instale el visor:</p>"
    f"<p><a href='{MALWARE_PATH}'>Descargar Invoice Viewer (Windows)</a></p>"
    "</body></html>"
)


class Handler(BaseHTTPRequestHandler):
    server_version = SERVER_BANNER
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        log(f"[web] {self.address_string()} {fmt % args} Host={self.headers.get('Host')}")

    def _send(self, code, body, ctype, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Server", SERVER_BANNER)
        for k, v in (extra or []):
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._send(200, LANDING.encode("utf-8"), "text/html; charset=utf-8")
        elif path == "/health":
            self._send(200, b"ok", "text/plain")
        elif path == MALWARE_PATH:
            log("[web] sirviendo el binario malicioso en claro")
            self._send(
                200, MALWARE,
                "application/octet-stream",
                extra=[("Content-Disposition",
                        'attachment; filename="Invoice_Viewer_Setup.exe"')],
            )
        else:
            self._send(404, b"Not Found", "text/plain")


MALWARE = build_malware(read_token())


def main():
    log(f"[web] {SERVER_BANNER} en 0.0.0.0:{PORT} (HTTP en claro)")
    log(f"[web] binario servido en {MALWARE_PATH} | token de {TOKEN_FILE}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

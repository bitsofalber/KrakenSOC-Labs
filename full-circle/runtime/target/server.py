#!/usr/bin/env python3
"""Servidor interno de Northwind: puertos abiertos (recon), login HTTP en claro y
un export sensible tras autenticacion. El fichero lleva la flag."""
import os
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

USER = os.environ.get("APP_USER", "svc_report")
PASS = os.environ.get("APP_PASS", "Rep0rt-Sync-2026")
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/export_token.txt")
SESSION = "9f2b7c1e0a4d"
EXTRA_PORTS = [22, 3306]


def read_token():
    try:
        with open(TOKEN_FILE, encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing}"


EXPORT = (
    "employee_id,name,salary_eur\n"
    "NW-201,A. Fields,84000\nNW-202,J. Okafor,79000\n"
    "# export_token: " + read_token() + "\n"
)
LOGIN = ("<html><body><h1>Northwind Reporting Portal</h1>"
         "<form method=POST action=/login><input name=username>"
         "<input name=password type=password><button>Sign in</button></form></body></html>")


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _s(self, code, body, ctype="text/html", extra=None):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        for k, v in (extra or []):
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", "/login"):
            self._s(200, LOGIN)
        elif p == "/health":
            self._s(200, "ok", "text/plain")
        elif p == "/admin/export.csv":
            if f"SID={SESSION}" in self.headers.get("Cookie", ""):
                self._s(200, EXPORT, "text/csv",
                        [("Content-Disposition", 'attachment; filename="export.csv"')])
            else:
                self._s(401, "auth required", "text/plain")
        else:
            self._s(404, "nf", "text/plain")

    def do_POST(self):
        if self.path != "/login":
            self._s(404, "nf", "text/plain")
            return
        n = int(self.headers.get("Content-Length", "0") or 0)
        f = parse_qs(self.rfile.read(n).decode())
        if f.get("username", [""])[0] == USER and f.get("password", [""])[0] == PASS:
            self._s(200, "<html><body>Welcome. <a href=/admin/export.csv>export</a></body></html>",
                    extra=[("Set-Cookie", f"SID={SESSION}; Path=/")])
        else:
            self._s(403, "bad creds", "text/plain")


def open_port(port):
    class Q(socketserver.BaseRequestHandler):
        def handle(self):
            try:
                self.request.sendall(b"SSH-2.0-OpenSSH_8.9\r\n" if port == 22 else b"5.7-MySQL\r\n")
            except OSError:
                pass
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer(("0.0.0.0", port), Q).serve_forever()


def main():
    for p in EXTRA_PORTS:
        threading.Thread(target=open_port, args=(p,), daemon=True).start()
    print("[target] HTTP :80 + puertos 22/3306 (recon), login + export sensible", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()


if __name__ == "__main__":
    main()

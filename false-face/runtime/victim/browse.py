#!/usr/bin/env python3
"""Victima: navega al gateway interno por HTTP en claro varias veces. Su trafico
(con el session_token) queda capturado en el segmento."""
import os
import socket
import time
import urllib.request

GATEWAY = os.environ.get("GATEWAY", "gateway")
START_DELAY = int(os.environ.get("START_DELAY", "9"))


def log(m):
    print(m, flush=True)


def main():
    time.sleep(START_DELAY)
    for _ in range(40):
        try:
            with socket.create_connection((GATEWAY, 80), timeout=2):
                break
        except OSError:
            time.sleep(1)
    for i in range(4):
        try:
            with urllib.request.urlopen(f"http://{GATEWAY}/admin", timeout=5) as r:
                r.read()
            log(f"[victim] GET http://{GATEWAY}/admin (en claro) #{i+1}")
        except Exception as e:
            log(f"[victim] error: {e}")
        time.sleep(1.5)
    log("[victim] navegacion completada.")
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Implante que hace beacon al C2 por TLS con un ClientHello de JA3 distintivo
(orden de ciphers fijo). El analista computa el JA3 para identificar la herramienta."""
import os
import socket
import ssl
import time

C2 = os.environ.get("C2_HOST", "c2server")
START_DELAY = int(os.environ.get("START_DELAY", "6"))
# Orden de ciphers FIJO -> ClientHello determinista -> JA3 estable/distintivo.
CIPHERS = "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:AES256-SHA:AES128-SHA"
SNI = "cdn.n0rthwind-static.com"


def log(m):
    print(m, flush=True)


def main():
    time.sleep(START_DELAY)
    for i in range(40):
        try:
            with socket.create_connection((C2, 443), timeout=3):
                break
        except OSError:
            time.sleep(1)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    ctx.set_ciphers(CIPHERS)
    for i in range(5):
        try:
            raw = socket.create_connection((C2, 443), timeout=5)
            s = ctx.wrap_socket(raw, server_hostname=SNI)
            log(f"[implant] beacon TLS #{i+1} (JA3 distintivo, SNI {SNI})")
            s.sendall(b"GET /submit HTTP/1.1\r\nHost: " + SNI.encode() + b"\r\n\r\n")
            s.recv(1024)
            s.close()
        except Exception as e:
            log(f"[implant] error: {e}")
        time.sleep(2)
    log("[implant] beaconing completado.")
    open("/tmp/session_done", "w").close()
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()

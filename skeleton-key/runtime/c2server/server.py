#!/usr/bin/env python3
"""
Servidor C2 sobre TLS de una intrusion en Northwind — descifrable.

El implante se comunica con este C2 por TLS. Pero el C2 esta MAL configurado:
usa un cipher con intercambio de claves RSA (TLS_RSA_WITH_AES_128_CBC_SHA, TLS
1.2) en vez de ECDHE. Eso significa SIN forward secrecy: quien tenga la clave
privada del servidor puede DESCIFRAR todo el trafico capturado. El equipo de IR
recupero esa clave (resources/decrypt-me.key). El tasking del C2 lleva la flag.

MITRE ATT&CK: T1573.002 (Encrypted Channel: Asymmetric Cryptography),
T1071.001 (Application Layer Protocol: Web).

NOTA DE MANTENEDOR: la flag va en el tasking y se lee de /seed/c2_token.txt. En
el repo es un DECOY; el token real se inyecta en CI desde SKELETON_KEY_TOKEN.
"""
import os
import socket
import ssl
import threading

TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/c2_token.txt")


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


def handle(conn):
    try:
        conn.recv(4096)  # peticion del implante (GET /task)
        token = read_token()
        body = (
            '{"task": "collect_and_exfil", "interval": 60, '
            f'"decrypt_key": "{token}", "note": "Northwind C2 tasking"}}'
        )
        resp = (
            "HTTP/1.1 200 OK\r\n"
            "Server: nginx\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n\r\n{body}"
        )
        conn.sendall(resp.encode())
    except OSError:
        pass
    finally:
        conn.close()


def main():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain("server.crt", "server.key")
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    # Cipher con key exchange RSA (sin ECDHE) -> descifrable con la clave privada.
    ctx.set_ciphers("AES128-SHA:@SECLEVEL=0")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 443))
    srv.listen(20)
    print("[c2] TLS C2 en 0.0.0.0:443 (RSA key exchange -> descifrable)", flush=True)
    while True:
        raw, _ = srv.accept()
        try:
            conn = ctx.wrap_socket(raw, server_side=True)
        except ssl.SSLError:
            raw.close()
            continue
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()

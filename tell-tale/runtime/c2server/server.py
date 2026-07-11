#!/usr/bin/env python3
"""
C2 sobre TLS de una intrusion en Northwind — identificable por su fingerprint.

El implante habla con este C2 por TLS. No lo desciframos (usa forward secrecy),
pero NO hace falta: el analisis se hace por METADATOS. El ClientHello del
implante tiene un JA3 distintivo (identifica la herramienta), y el CERTIFICADO
que presenta el servidor viaja en CLARO en el handshake — su Subject (campo O)
lleva la flag.

MITRE ATT&CK: T1573.002 (Encrypted Channel), T1071.001 (Web Protocols).

NOTA DE MANTENEDOR: la flag va en el Subject del certificado (campo O). En el
repo el cert lleva un DECOY; el CI regenera el cert con la flag real desde el
secret TELL_TALE_TOKEN (ver README y el workflow release)."""
import socket
import ssl
import threading


def handle(conn):
    try:
        conn.recv(2048)
        conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
    except OSError:
        pass
    finally:
        conn.close()


def main():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain("server.crt", "server.key")
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 443))
    srv.listen(20)
    print("[c2] TLS C2 en 0.0.0.0:443 (cert con la flag en el Subject)", flush=True)
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

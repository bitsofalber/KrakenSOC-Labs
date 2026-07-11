#!/usr/bin/env python3
"""
Resolver DNS-over-HTTPS (DoH) malicioso de una intrusion en Northwind.

El implante hace consultas DoH (DNS sobre HTTPS, GET /resolve?name=...) hacia este
resolver. Al ir el DNS dentro de HTTPS, un firewall/proxy DNS normal NO lo ve: es
un canal de exfiltracion encubierto (DoH). Cada consulta lleva un trozo de los
datos exfiltrados en el subdominio del ?name=. El servidor usa key exchange RSA
(descifrable con resources/decrypt-me.key), asi el IR reconstruye las consultas.

MITRE ATT&CK: T1572 (Protocol Tunneling), T1048.003 (Exfil Over Unencrypted...
aqui sobre HTTPS pero canal no-C2), T1071.004 (DNS).

NOTA: la flag va troceada en los ?name= (la manda el implante). El token se lee
de /seed/doh_token.txt; en el repo es DECOY, el CI inyecta el real (DARK_WATER_TOKEN)."""
import socket
import ssl
import threading


def handle(conn):
    try:
        conn.recv(4096)
        body = '{"Status":0,"Answer":[{"name":"x","type":1,"data":"10.0.0.1"}]}'
        conn.sendall((
            "HTTP/1.1 200 OK\r\nContent-Type: application/dns-json\r\n"
            f"Content-Length: {len(body)}\r\n\r\n{body}"
        ).encode())
    except OSError:
        pass
    finally:
        conn.close()


def main():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain("server.crt", "server.key")
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    ctx.set_ciphers("AES128-SHA:@SECLEVEL=0")  # RSA key exchange -> descifrable
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 443))
    srv.listen(20)
    print("[doh] resolver DoH en 0.0.0.0:443 (TLS RSA, descifrable)", flush=True)
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

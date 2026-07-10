#!/usr/bin/env python3
"""
Servidor objetivo de Northwind con varios servicios expuestos.

Abre un conjunto FIJO de puertos TCP. Un atacante en la red lo escanea (Nmap)
para descubrir sus servicios — reconocimiento. Como el escaneo genera tráfico,
queda capturado en el PCAP. Uno de los servicios (el panel de administración en
8080) devuelve un banner con una service-key: ese es el objetivo del lab.

MITRE ATT&CK: T1046 (Network Service Discovery), T1595 (Active Scanning).

NOTA DE MANTENEDOR: la service-key (la flag) va en el banner del 8080 y se lee de
/seed/service_key.txt. En el repositorio es un DECOY; el token real se inyecta en
el build de CI desde un secret (ver README y el workflow release).
"""
import os
import socketserver
import threading

TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/service_key.txt")


def log(msg):
    print(msg, flush=True)


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


TOKEN = read_token()

# Puertos abiertos y su banner (se envia al conectar, para que Nmap -sV lo lea).
# El 8080 (panel de admin) filtra la service-key. El resto son ruido realista.
BANNERS = {
    22: "SSH-2.0-OpenSSH_8.9p1 Northwind\r\n",
    80: "HTTP/1.0 200 OK\r\nServer: Northwind-Web/1.4\r\nContent-Length: 0\r\n\r\n",
    3306: "5.7.40-Northwind-MySQL\r\n",
    8080: f"220 Northwind Admin Console 1.2 ready service-key={TOKEN}\r\n",
}


class BannerHandler(socketserver.BaseRequestHandler):
    banner = ""

    def handle(self):
        try:
            self.request.sendall(self.banner.encode("utf-8"))
            # Deja la conexion un instante para que Nmap capte el servicio.
            self.request.settimeout(2)
            try:
                self.request.recv(256)
            except OSError:
                pass
        except OSError:
            pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve(port, banner):
    handler = type("H", (BannerHandler,), {"banner": banner})
    Server(("0.0.0.0", port), handler).serve_forever()


def main():
    log(f"[target] abriendo puertos: {sorted(BANNERS)} (8080 filtra la service-key)")
    threads = []
    for port, banner in BANNERS.items():
        t = threading.Thread(target=serve, args=(port, banner), daemon=True)
        t.start()
        threads.append(t)
    log("[target] listo. Esperando el escaneo del atacante...")
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Servidor FTP legacy de Northwind Global Systems — "Sales File Drop".

Un servidor de intercambio de ficheros interno que nunca se migró a SFTP/FTPS:
sigue sirviendo por FTP EN CLARO (puerto 21). Las credenciales (USER/PASS) y
toda la transferencia de datos viajan legibles por la red. El objetivo del
laboratorio es que el alumno, a partir del PCAP, recupere:
  - las credenciales del canal de control (comandos USER/PASS en claro), y
  - el fichero exfiltrado del canal de datos (RETR), que lleva la flag.

MITRE ATT&CK: T1040 (Network Sniffing), T1078 (Valid Accounts),
T1048.003 (Exfiltration Over Unencrypted Non-C2 Protocol).

NOTA DE MANTENEDOR: el token (la flag) se lee de /seed/export_token.txt. En el
repositorio ese fichero es un DECOY; el token real se inyecta solo en el build
de CI desde un secret (ver runtime/ftp-server/README.md y el workflow release).
"""
import os
import socket

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

PORT = int(os.environ.get("FTP_PORT", "21"))
FTP_USER = os.environ.get("FTP_USER", "svc_fileshare").strip()
FTP_PASS = os.environ.get("FTP_PASS", "Rw-Fileshare-2026").strip()
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/export_token.txt")
DATA_DIR = os.environ.get("DATA_DIR", "/srv/data")
# Rango de puertos pasivos PINEADO: así el sniffer sabe qué capturar y el canal
# de datos es determinista en cada despliegue.
PASV_LOW, PASV_HIGH = 30000, 30009

BANNER = "Northwind Global Systems FTP Service (vsFTPd 3.0-compatible)"


def log(msg):
    print(msg, flush=True)


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


def build_data_dir(token):
    """Construye el fichero sensible (con la flag embebida) + uno benigno."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # Fichero benigno, para que el listado parezca un share real.
    with open(os.path.join(DATA_DIR, "README.txt"), "w", encoding="utf-8") as fh:
        fh.write(
            "Northwind Global Systems — Sales File Drop\r\n"
            "Uso interno. Migracion a SFTP pendiente (ticket IT-4471).\r\n"
        )

    # El fichero exfiltrado: un export de clientes con la flag en el pie como
    # "token de exportacion". El alumno debe reconstruir el fichero del canal de
    # datos y localizar el token.
    rows = [
        "customer_id,company,contact,tier,annual_value_eur",
        "NW-1001,Meridian Logistics,A. Fields,Platinum,1240000",
        "NW-1002,Cormorant Freight,J. Okafor,Gold,880000",
        "NW-1003,Halden Manufacturing,P. Reyes,Gold,760000",
        "NW-1004,Blue Harbor Retail,S. Nakamura,Silver,410000",
        "NW-1005,Aster Pharmaceuticals,L. Bianchi,Platinum,1510000",
        "NW-1006,Vantage Energy,D. Mbeki,Gold,690000",
        "# ---- EXPORT MANIFEST (internal use only) ----",
        "# generated_by: svc_fileshare",
        "# classification: CONFIDENTIAL",
        f"# export_token: {token}",
    ]
    with open(os.path.join(DATA_DIR, "customers_q4_export.csv"), "w",
              encoding="utf-8") as fh:
        fh.write("\r\n".join(rows) + "\r\n")


def my_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return "127.0.0.1"


def main():
    token = read_token()
    build_data_dir(token)

    authorizer = DummyAuthorizer()
    # Permisos de solo lectura: e=CWD, l=LIST, r=RETR (descarga). Sin escritura.
    authorizer.add_user(FTP_USER, FTP_PASS, DATA_DIR, perm="elr")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = BANNER
    # PASV: anuncia la IP del propio contenedor (el cliente lo alcanza por la
    # red del lab) y un rango de puertos fijo que el sniffer captura.
    handler.masquerade_address = my_ip()
    handler.passive_ports = range(PASV_LOW, PASV_HIGH + 1)

    log(f"[ftp] {BANNER}")
    log(f"[ftp] escuchando en 0.0.0.0:{PORT} (FTP EN CLARO)")
    log(f"[ftp] cuenta valida: {FTP_USER} | token cargado de {TOKEN_FILE}")
    log(f"[ftp] PASV masquerade={handler.masquerade_address} "
        f"ports={PASV_LOW}-{PASV_HIGH}")

    server = FTPServer(("0.0.0.0", PORT), handler)
    server.serve_forever()


if __name__ == "__main__":
    main()

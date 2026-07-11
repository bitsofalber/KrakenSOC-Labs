#!/usr/bin/env python3
"""Cliente SMB de un empleado de Northwind: se autentica por NTLM y lee un
fichero del share de Finanzas. El handshake NTLMSSP y la lectura quedan en el PCAP."""
import io
import os
import socket
import time
from impacket.smbconnection import SMBConnection

SMB_HOST = os.environ.get("SMB_HOST", "smbserver")
SMB_USER = os.environ.get("SMB_USER", "m.calloway")
SMB_PASS = os.environ.get("SMB_PASS", "Autumn-2026-Finance")
SMB_DOMAIN = os.environ.get("SMB_DOMAIN", "NORTHWIND")
START_DELAY = int(os.environ.get("START_DELAY", "8"))


def log(m):
    print(m, flush=True)


def wait(retries=40):
    for _ in range(retries):
        try:
            with socket.create_connection((SMB_HOST, 445), timeout=2):
                return
        except OSError:
            time.sleep(1)
    raise SystemExit("[client] smb no responde")


def main():
    time.sleep(START_DELAY)
    wait()
    log(f"[client] conectando a //{SMB_HOST}/FINANCE como {SMB_DOMAIN}\\{SMB_USER} (NTLM)")
    conn = SMBConnection(SMB_HOST, SMB_HOST, sess_port=445, timeout=15)
    conn.login(SMB_USER, SMB_PASS, domain=SMB_DOMAIN)
    log("[client] autenticado. Listando y leyendo el share...")
    conn.listPath("FINANCE", "*")
    buf = io.BytesIO()
    conn.getFile("FINANCE", "Payroll_Q4_2026.txt", buf.write)
    log(f"[client] leido Payroll_Q4_2026.txt ({buf.tell()} bytes)")
    conn.logoff()
    log("[client] flujo completado. Fin.")
    open("/tmp/session_done", "w").close()
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()

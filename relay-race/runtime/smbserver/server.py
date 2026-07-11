#!/usr/bin/env python3
"""
Servidor de ficheros SMB de Northwind — el share de Finanzas.

Un servidor SMB donde los empleados guardan documentos. El cliente se autentica
con NTLM: en el handshake (NTLMSSP) viajan el usuario, el dominio/estacion y la
respuesta NTLMv2 (el "hash" que un atacante capturaria para crackear o relay).
El fichero al que accede el cliente lleva un secreto. Todo queda en el PCAP.

MITRE ATT&CK: T1040 (Network Sniffing), T1557.001 (LLMNR/NBT-NS/NTLM capture),
T1021.002 (SMB/Windows Admin Shares).

NOTA DE MANTENEDOR: la flag va en un fichero del share y se lee de
/seed/share_token.txt. En el repo es un DECOY; el token real se inyecta en CI
desde el secret RELAY_RACE_TOKEN.
"""
import os
from impacket import smbserver

SHARE = "FINANCE"
SHARE_DIR = "/srv/share"
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/share_token.txt")


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


def build_share():
    os.makedirs(SHARE_DIR, exist_ok=True)
    with open(os.path.join(SHARE_DIR, "README.txt"), "w", encoding="utf-8") as fh:
        fh.write("Northwind Finance share. Uso interno.\r\n")
    with open(os.path.join(SHARE_DIR, "Payroll_Q4_2026.txt"), "w", encoding="utf-8") as fh:
        fh.write(
            "Northwind Global Systems - Payroll Q4 2026 (CONFIDENTIAL)\r\n"
            f"vault_token: {read_token()}\r\n"
        )


def main():
    build_share()
    print(f"[smb] Northwind FINANCE share en //0.0.0.0/{SHARE} (SMB2, NTLM)", flush=True)
    server = smbserver.SimpleSMBServer(listenAddress="0.0.0.0", listenPort=445)
    server.addShare(SHARE, SHARE_DIR, "Northwind Finance Share")
    server.setSMB2Support(True)
    server.setSMBChallenge("")
    server.start()


if __name__ == "__main__":
    main()

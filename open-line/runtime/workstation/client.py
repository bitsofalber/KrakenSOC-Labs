#!/usr/bin/env python3
"""
Estacion del operador de red (NetOps) de Northwind.

Simula a un administrador conectandose por Telnet EN CLARO al router core legacy
para revisar la configuracion. Como Telnet no cifra nada, el usuario, la
contrasena y toda la salida (incluida una service-key) quedan legibles en la
captura. El sniffer graba la sesion.

No hay exploit: el fallo es administrar por Telnet en vez de SSH. Punto
didactico — MITRE ATT&CK T1040 (Network Sniffing) y T1078 (Valid Accounts).
"""
import os
import socket
import time

TELNET_HOST = os.environ.get("TELNET_HOST", "telnetd")
TELNET_PORT = int(os.environ.get("TELNET_PORT", "23"))
TELNET_USER = os.environ.get("TELNET_USER", "netops")
TELNET_PASS = os.environ.get("TELNET_PASS", "NetOps-2026-RtrAdmin")
START_DELAY = int(os.environ.get("START_DELAY", "6"))


def log(msg):
    print(msg, flush=True)


def wait_for(retries=40):
    for _ in range(retries):
        try:
            with socket.create_connection((TELNET_HOST, TELNET_PORT), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    raise SystemExit(f"[workstation] telnet {TELNET_HOST}:{TELNET_PORT} no responde")


def main():
    time.sleep(START_DELAY)
    wait_for()
    log(f"[workstation] telnet {TELNET_HOST}:{TELNET_PORT} (EN CLARO) como '{TELNET_USER}'")
    s = socket.create_connection((TELNET_HOST, TELNET_PORT), timeout=10)
    s.settimeout(5)

    def send(line):
        s.sendall((line + "\r\n").encode("utf-8"))
        time.sleep(0.4)

    def drain():
        try:
            while True:
                data = s.recv(4096)
                if not data:
                    break
        except socket.timeout:
            pass

    # Login (usuario y contrasena en claro)
    time.sleep(0.5)
    send(TELNET_USER)
    send(TELNET_PASS)
    time.sleep(0.4)
    # Sesion de administracion: ver version y volcar la config (con la key)
    log("[workstation] ejecutando 'show version' y 'show running-config'...")
    send("show version")
    time.sleep(0.4)
    send("show running-config")
    time.sleep(0.6)
    send("exit")
    drain()
    s.close()
    log("[workstation] sesion Telnet cerrada. Flujo completado. Fin.")


if __name__ == "__main__":
    main()

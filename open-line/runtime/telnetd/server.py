#!/usr/bin/env python3
"""
Router core legacy de Northwind Global Systems — acceso por Telnet EN CLARO.

Un equipo de red antiguo que sigue administrandose por Telnet (puerto 23) en vez
de SSH. Toda la sesion viaja legible: el usuario, la contrasena y la salida de
los comandos. Cuando el operador ejecuta 'show running-config', el equipo vuelca
su configuracion — incluida una service-key (la flag) — en claro por la red.

MITRE ATT&CK: T1040 (Network Sniffing), T1078 (Valid Accounts).

NOTA DE MANTENEDOR: la service-key (la flag) se lee de /seed/service_key.txt. En
el repositorio ese fichero es un DECOY; la key real se inyecta solo en el build
de CI desde un secret (ver runtime/telnetd/README.md y el workflow release).
"""
import os
import socketserver

PORT = int(os.environ.get("TELNET_PORT", "23"))
TELNET_USER = os.environ.get("TELNET_USER", "netops").strip()
TELNET_PASS = os.environ.get("TELNET_PASS", "NetOps-2026-RtrAdmin").strip()
KEY_FILE = os.environ.get("KEY_FILE", "/seed/service_key.txt")
HOSTNAME = "nw-core-rtr01"

BANNER = (
    "\r\nNorthwind Global Systems - Core Router (IOS-legacy 12.4)\r\n"
    "Unauthorized access is prohibited.\r\n\r\n"
)
VERSION = (
    "Northwind IOS (tm) Software, Version 12.4(25b), RELEASE\r\n"
    "nw-core-rtr01 uptime is 412 days\r\n"
    "System image: flash:c2800-adventerprisek9-mz.124-25b.bin\r\n"
)


def log(msg):
    print(msg, flush=True)


def read_key():
    try:
        with open(KEY_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_key}"


SERVICE_KEY = read_key()


def running_config():
    return (
        "Building configuration...\r\n\r\n"
        "Current configuration : 1284 bytes\r\n"
        "!\r\n"
        "hostname nw-core-rtr01\r\n"
        "!\r\n"
        "enable secret 5 $1$mERr$legacyHashRedacted\r\n"
        "!\r\n"
        f"username {TELNET_USER} privilege 15 password 0 {TELNET_PASS}\r\n"
        "!\r\n"
        "interface GigabitEthernet0/0\r\n"
        " ip address 10.20.0.1 255.255.255.0\r\n"
        "!\r\n"
        "snmp-server community northwind-ro RO\r\n"
        f"service-key {SERVICE_KEY}\r\n"
        "!\r\n"
        "line vty 0 4\r\n"
        " transport input telnet\r\n"
        "!\r\n"
        "end\r\n"
    )


class TelnetHandler(socketserver.StreamRequestHandler):
    def _w(self, text):
        self.wfile.write(text.encode("utf-8"))
        self.wfile.flush()

    def _readline(self):
        line = self.rfile.readline()
        return line.decode("utf-8", "replace").strip()

    def handle(self):
        self._w(BANNER)
        self._w("Username: ")
        user = self._readline()
        self._w("Password: ")
        pw = self._readline()
        log(f"[telnetd] intento de login user='{user}'")
        if user != TELNET_USER or pw != TELNET_PASS:
            self._w("\r\n% Authentication failed.\r\n")
            return
        log("[telnetd] login OK -> shell privilegiada (en claro)")
        self._w(f"\r\n{HOSTNAME}> ")
        while True:
            cmd = self._readline()
            if cmd in ("exit", "quit", "logout"):
                self._w("\r\nConnection closed by foreign host.\r\n")
                break
            if cmd == "show version":
                self._w(VERSION)
            elif cmd in ("show running-config", "show run"):
                self._w(running_config())
            elif cmd == "":
                pass
            else:
                self._w(f"% Invalid input: {cmd}\r\n")
            self._w(f"\r\n{HOSTNAME}> ")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    log(f"[telnetd] Telnet EN CLARO en 0.0.0.0:{PORT} (host {HOSTNAME})")
    log(f"[telnetd] cuenta valida: {TELNET_USER} | key cargada de {KEY_FILE}")
    Server(("0.0.0.0", PORT), TelnetHandler).serve_forever()


if __name__ == "__main__":
    main()

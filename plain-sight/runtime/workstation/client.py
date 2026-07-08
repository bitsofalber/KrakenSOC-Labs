#!/usr/bin/env python3
"""
Estación de trabajo de un empleado de Northwind (Sales).

Simula a un usuario real usando el portal interno legacy por HTTP: primero
navega por unas cuantas páginas benignas y después inicia sesión enviando sus
credenciales EN CLARO (POST /login urlencoded). Con la cookie de sesión que
recibe, abre el panel. Todo ese tráfico lo captura el sniffer: las credenciales
y el token de sesión quedan legibles en el PCAP.

No hay nada "malicioso" en el cliente: el fallo es el protocolo sin cifrar. Ese
es justo el punto didáctico (MITRE ATT&CK T1040 Network Sniffing).
"""
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

PORTAL_HOST = os.environ.get("PORTAL_HOST", "portal")
PORTAL_PORT = int(os.environ.get("PORTAL_PORT", "80"))
PORTAL_USER = os.environ.get("PORTAL_USER", "s.buchanan")
PORTAL_PASS = os.environ.get("PORTAL_PASS", "S@lesManager2026")
START_DELAY = int(os.environ.get("START_DELAY", "6"))

BASE = f"http://{PORTAL_HOST}:{PORTAL_PORT}"
BENIGN_PATHS = ["/", "/assets/style.css", "/about", "/favicon.ico", "/help"]


def log(msg):
    print(msg, flush=True)


def wait_for_portal(retries=40):
    for _ in range(retries):
        try:
            with socket.create_connection((PORTAL_HOST, PORTAL_PORT), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    raise SystemExit(f"[workstation] el portal {BASE} no responde")


def get(path, headers=None):
    req = urllib.request.Request(BASE + path, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()
            return resp
    except urllib.error.HTTPError as e:
        e.read()
        return e


def browse_benign():
    log("[workstation] navegación benigna por la intranet...")
    for p in BENIGN_PATHS:
        get(p)
        time.sleep(0.4)


def login():
    log(f"[workstation] iniciando sesión como '{PORTAL_USER}' (HTTP en claro)")
    body = urllib.parse.urlencode(
        {"username": PORTAL_USER, "password": PORTAL_PASS}
    ).encode("ascii")
    req = urllib.request.Request(
        BASE + "/login",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        resp.read()
        cookie = resp.headers.get("Set-Cookie", "")
    session = ""
    for part in cookie.split(","):
        if "SESSIONID=" in part:
            session = part.split("SESSIONID=", 1)[1].split(";", 1)[0]
    log(f"[workstation] sesión establecida (SESSIONID={session or 'n/a'})")
    return session


def open_dashboard(session):
    headers = {"Cookie": f"SESSIONID={session}", "X-Portal-User": PORTAL_USER}
    get("/dashboard", headers=headers)
    log("[workstation] panel abierto con la cookie de sesión.")


def main():
    time.sleep(START_DELAY)
    wait_for_portal()
    browse_benign()
    session = login()
    time.sleep(0.5)
    open_dashboard(session)
    # Un poco más de ruido para que la sesión no sea el único tráfico.
    for p in ("/", "/help"):
        get(p)
        time.sleep(0.3)
    log("[workstation] flujo completado. Fin.")


if __name__ == "__main__":
    main()

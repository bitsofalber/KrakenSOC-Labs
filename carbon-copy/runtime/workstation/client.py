#!/usr/bin/env python3
"""
Estacion que envia el correo de phishing a traves del relay SMTP en claro.

Simula la entrega de un spearphishing con adjunto malicioso pasando por el relay
SMTP legacy de Northwind (sin cifrar). Como el SMTP va en claro, el remitente, el
destinatario, el asunto, el cuerpo y el adjunto (base64) quedan legibles en el
PCAP. El analista recupera las cabeceras y decodifica el adjunto para sacar la
flag.

MITRE ATT&CK: T1566.001 (Spearphishing Attachment), T1040 (Network Sniffing).

NOTA DE MANTENEDOR: la flag va embebida en el adjunto y se lee de
/seed/mail_token.txt. En el repositorio ese fichero es un DECOY; el token real se
inyecta solo en el build de CI desde un secret (ver README y el workflow release).
"""
import os
import smtplib
import socket
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = os.environ.get("SMTP_HOST", "smtpd")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))
START_DELAY = int(os.environ.get("START_DELAY", "6"))
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/seed/mail_token.txt")

MAIL_FROM = "accounts@northw1nd-billing.com"   # dominio typosquat (1 en vez de i)
MAIL_TO = "s.buchanan@northwind.example"
SUBJECT = "Factura pendiente Q4 - accion requerida"
ATTACH_NAME = "Factura_Q4_2026.html"

BODY = (
    "Estimado cliente,\r\n\r\n"
    "Adjuntamos la factura pendiente del Q4. Por favor, abra el documento "
    "adjunto y confirme el pago antes de 48h para evitar la suspension del "
    "servicio.\r\n\r\n"
    "Departamento de Facturacion\r\n"
)


def log(msg):
    print(msg, flush=True)


def read_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{missing_token}"


def wait_for(retries=40):
    for _ in range(retries):
        try:
            with socket.create_connection((SMTP_HOST, SMTP_PORT), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    raise SystemExit(f"[workstation] smtp {SMTP_HOST}:{SMTP_PORT} no responde")


def build_message(token):
    # El adjunto malicioso: un HTML con la flag embebida como verification-token.
    attachment = (
        "<html><body>\n"
        "<h1>Northwind Global Systems - Factura Q4 2026</h1>\n"
        "<p>Documento de facturacion. Habilite las macros para ver el detalle.</p>\n"
        f"<!-- verification-token: {token} -->\n"
        "</body></html>\n"
    )
    msg = MIMEMultipart()
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(BODY, "plain"))
    part = MIMEApplication(attachment.encode("utf-8"), Name=ATTACH_NAME)
    part["Content-Disposition"] = f'attachment; filename="{ATTACH_NAME}"'
    msg.attach(part)
    return msg


def main():
    time.sleep(START_DELAY)
    wait_for()
    token = read_token()
    msg = build_message(token)
    log(f"[workstation] enviando phishing por SMTP {SMTP_HOST}:{SMTP_PORT} (EN CLARO)")
    log(f"[workstation]   From: {MAIL_FROM}  To: {MAIL_TO}")
    log(f"[workstation]   Subject: {SUBJECT}  Adjunto: {ATTACH_NAME}")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
    # NO se llama a starttls(): la sesion queda en claro (el punto del lab).
    server.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())
    server.quit()
    log("[workstation] correo entregado. Flujo completado. Fin.")


if __name__ == "__main__":
    main()

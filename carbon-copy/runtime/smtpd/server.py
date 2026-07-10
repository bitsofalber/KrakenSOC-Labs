#!/usr/bin/env python3
"""
Relay SMTP interno legacy de Northwind Global Systems — EN CLARO (puerto 25).

Un servidor de correo antiguo que acepta SMTP sin cifrar y sin STARTTLS: todo el
mensaje (remitente, destinatario, asunto, cuerpo y adjuntos) viaja legible por la
red. En este laboratorio, un correo de phishing con un adjunto malicioso pasa por
el relay y queda capturado en claro. El objetivo es que el alumno recupere las
cabeceras del correo y decodifique el adjunto (base64) para sacar la flag.

MITRE ATT&CK: T1040 (Network Sniffing), T1566.001 (Spearphishing Attachment).

Servidor minimo en stdlib (socketserver): implementa lo justo del protocolo SMTP
para que un cliente smtplib entregue el mensaje. NO anuncia STARTTLS a proposito
— asi la sesion permanece en claro (el punto didactico).
"""
import os
import socketserver

PORT = int(os.environ.get("SMTP_PORT", "25"))
HOSTNAME = "mail-relay01.northwind.local"


def log(msg):
    print(msg, flush=True)


class SMTPHandler(socketserver.StreamRequestHandler):
    def _w(self, text):
        self.wfile.write((text + "\r\n").encode("utf-8"))
        self.wfile.flush()

    def _readline(self):
        return self.rfile.readline().decode("utf-8", "replace").rstrip("\r\n")

    def handle(self):
        self._w(f"220 {HOSTNAME} ESMTP NorthwindMail (legacy, no TLS)")
        in_data = False
        while True:
            line = self._readline()
            if line == "" and not in_data:
                if not self.rfile.peek(1):
                    break
                continue
            upper = line.upper()
            if in_data:
                # Fin de DATA: una linea con solo un punto.
                if line == ".":
                    in_data = False
                    self._w("250 2.0.0 Ok: queued as ABC123")
                continue
            if upper.startswith("EHLO") or upper.startswith("HELO"):
                # Respuesta multilinea SIN STARTTLS -> el cliente no cifra.
                self._w(f"250-{HOSTNAME} greets you")
                self._w("250-8BITMIME")
                self._w("250 SIZE 10485760")
            elif upper.startswith("MAIL FROM"):
                log(f"[smtpd] {line}")
                self._w("250 2.1.0 Ok")
            elif upper.startswith("RCPT TO"):
                log(f"[smtpd] {line}")
                self._w("250 2.1.5 Ok")
            elif upper == "DATA":
                self._w("354 End data with <CR><LF>.<CR><LF>")
                in_data = True
            elif upper.startswith("RSET"):
                self._w("250 2.0.0 Ok")
            elif upper.startswith("NOOP"):
                self._w("250 2.0.0 Ok")
            elif upper.startswith("QUIT"):
                self._w("221 2.0.0 Bye")
                break
            else:
                self._w("250 2.0.0 Ok")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    log(f"[smtpd] SMTP EN CLARO en 0.0.0.0:{PORT} (host {HOSTNAME}, sin STARTTLS)")
    Server(("0.0.0.0", PORT), SMTPHandler).serve_forever()


if __name__ == "__main__":
    main()

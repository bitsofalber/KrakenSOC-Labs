#!/usr/bin/env python3
"""
Data-forge de Battering Ram — genera un dataset de ataques de autenticación
sobre el dominio Windows de Northwind y lo ingesta en Splunk vía HEC
(índice 'northwind').

Escenario: un atacante externo lanza password spraying (una contraseña común
contra muchas cuentas) y fuerza bruta dirigida (muchas contraseñas contra una
cuenta), provoca bloqueos de cuenta y acaba consiguiendo UN inicio de sesión
válido. Con ese acceso crea una cuenta backdoor y la mete en Administradores, y
ejecuta un comando ofuscado (donde va la flag). El alumno lo caza con SPL sobre
los logs de seguridad de Windows.

Fuentes: WinEventLog:Security (4625 fallo, 4740 lockout, 4624 éxito, 4720 alta
de cuenta, 4732 alta en grupo) y Sysmon EventID=1 (comandos post-explotación).

Todo es SINTÉTICO y REPRODUCIBLE (seed fija). En el repo, /seed/flag.txt es un
DECOY; el valor real se inyecta en el build de CI desde un secret.
"""
import base64
import json
import os
import random
import time
import urllib.error
import urllib.request

HEC_URL = os.environ.get("HEC_URL", "https://splunk:8088/services/collector/event")
HEC_TOKEN = os.environ.get("HEC_TOKEN", "00000000-0000-0000-0000-000000000000")
INDEX = os.environ.get("SPLUNK_INDEX", "northwind")
SEED = int(os.environ.get("FORGE_SEED", "4625"))
MGMT_URL = os.environ.get("SPLUNK_MGMT_URL", "https://splunk:8089")
SPLUNK_USER = os.environ.get("SPLUNK_USER", "admin")
SPLUNK_PASSWORD = os.environ.get("SPLUNK_PASSWORD", "Changeme123!")


def _load_flag():
    v = os.environ.get("BATTERING_RAM_FLAG")
    if v:
        return v.strip()
    try:
        with open("/seed/flag.txt", "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{th15_15_n0t_th3_r34l_fl4g}"


FLAG = _load_flag()
rng = random.Random(SEED)

DOMAIN = "NWGLOBAL"
ATTACKER_IP = "45.83.220.50"                      # IP del atacante (spray + brute)
TARGET_HOST = "NW-SRV-APP01"                      # host donde entra
COMPROMISED = "svc_reporting"                     # cuenta con contraseña débil que cae
BRUTE_TARGET = "administrator"                    # cuenta objetivo de la fuerza bruta
BACKDOOR = "support"                              # cuenta backdoor que crea el atacante

# Cuentas de la flota rociadas (password spraying: 1 contraseña, N cuentas)
SPRAY_ACCOUNTS = [
    "nancy.davolio", "a.fuller", "j.leverling", "m.peacock", "s.buchanan",
    "m.suyama", "r.king", "l.callahan", "svc_backup", COMPROMISED,
    "svc_sql", "helpdesk", "p.cramer", "h.bennett", "y.tannamuri",
    "t.hardy", "l.lebihan", "r.mendel",
]
BENIGN_USERS = ["nancy.davolio", "a.fuller", "j.leverling", "m.peacock", "r.king"]
FLEET = [f"NW-WKS-{i:03d}" for i in range(1, 40)] + ["NW-SRV-DC01", "NW-SRV-APP01", "NW-SRV-FS01"]

T0 = time.time() - 3600
events = []


def b64(s):
    return base64.b64encode(s.encode()).decode()


def add(sourcetype, ts, fields):
    events.append({
        "time": round(ts, 3),
        "host": fields.get("Computer", "NW-DC"),
        "source": "northwind:forge",
        "sourcetype": sourcetype,
        "index": INDEX,
        "event": fields,
    })


def sec(ts, code, account, computer, src="", logon_type="", status="", signature="", extra=None):
    f = {
        "EventCode": code, "Account_Name": account, "Computer": computer,
        "signature": signature,
    }
    if src:
        f["Source_Network_Address"] = src
    if logon_type != "":
        f["Logon_Type"] = logon_type
    if status:
        f["Sub_Status"] = status
    if extra:
        f.update(extra)
    add("WinEventLog:Security", ts, f)


# ── Ruido benigno: logins normales y algún fallo de dedo ─────────────────────
def forge_benign():
    for _ in range(70):
        ts = T0 + rng.uniform(0, 3300)
        sec(ts, 4624, rng.choice(BENIGN_USERS), rng.choice(FLEET),
            src=f"10.30.{rng.randint(1,40)}.{rng.randint(2,254)}",
            logon_type=rng.choice([2, 3, 7]),
            signature="An account was successfully logged on")
    for _ in range(6):  # fallos legítimos aislados (contraseña mal tecleada)
        ts = T0 + rng.uniform(0, 3300)
        sec(ts, 4625, rng.choice(BENIGN_USERS), rng.choice(FLEET),
            src=f"10.30.{rng.randint(1,40)}.{rng.randint(2,254)}",
            logon_type=2, status="0xC000006A",
            signature="An account failed to log on")


# ── Ataque de autenticación ──────────────────────────────────────────────────
def forge_attack():
    t = T0 + 300

    # 1) PASSWORD SPRAYING: una contraseña contra muchas cuentas (1 intento c/u)
    for i, acct in enumerate(SPRAY_ACCOUNTS):
        sec(t + i * 6, 4625, acct, "NW-SRV-DC01", src=ATTACKER_IP, logon_type=3,
            status="0xC000006A", signature="An account failed to log on")

    # 2) FUERZA BRUTA dirigida contra 'administrator' (muchos intentos)
    tb = t + len(SPRAY_ACCOUNTS) * 6 + 30
    for i in range(18):
        sec(tb + i * 4, 4625, BRUTE_TARGET, "NW-SRV-DC01", src=ATTACKER_IP, logon_type=3,
            status="0xC000006A", signature="An account failed to log on")
    # administrator se bloquea
    sec(tb + 18 * 4 + 5, 4740, BRUTE_TARGET, "NW-SRV-DC01",
        signature="A user account was locked out",
        extra={"Caller_Computer_Name": "NW-SRV-DC01"})

    # 3) Otras 2 cuentas también se bloquean por el spray repetido
    for acct in ("svc_backup", "helpdesk"):
        for i in range(6):
            sec(tb + 100 + i * 3, 4625, acct, "NW-SRV-DC01", src=ATTACKER_IP, logon_type=3,
                status="0xC000006A", signature="An account failed to log on")
        sec(tb + 100 + 6 * 3 + 4, 4740, acct, "NW-SRV-DC01",
            signature="A user account was locked out")

    # 4) ÉXITO: svc_reporting (contraseña débil) cae y el atacante entra
    ts = tb + 200
    sec(ts, 4624, COMPROMISED, TARGET_HOST, src=ATTACKER_IP, logon_type=10,
        signature="An account was successfully logged on",
        extra={"Authentication_Package": "NTLM"})

    # 5) POST-EXPLOTACIÓN en el host comprometido
    def sysmon(ts_, cmd, parent="cmd.exe"):
        add("Sysmon", ts_, {
            "EventID": 1, "Computer": TARGET_HOST, "User": f"{DOMAIN}\\{COMPROMISED}",
            "Image": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "ParentImage": rf"C:\Windows\System32\{parent}",
            "CommandLine": cmd, "ProcessId": rng.randint(3000, 8000),
        })

    sysmon(ts + 30, f"powershell.exe net user {BACKDOOR} P@ssw0rd123! /add")
    sec(ts + 32, 4720, BACKDOOR, TARGET_HOST,
        signature="A user account was created")
    sysmon(ts + 60, f"powershell.exe net localgroup administrators {BACKDOOR} /add")
    sec(ts + 62, 4732, BACKDOOR, TARGET_HOST,
        signature="A member was added to a security-enabled global group",
        extra={"Group_Name": "Administrators"})

    # 6) Comando ofuscado con la FLAG
    flag_script = f"$op='post-auth';Write-Output '{FLAG}'"
    sysmon(ts + 90, f"powershell.exe -NoProfile -EncodedCommand {b64(flag_script)}",
           parent="powershell.exe")


# ── Ingesta HEC (mismo patrón que Poltergeist/Overwatch) ─────────────────────
def _ssl_ctx():
    import ssl
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c


def _auth_header():
    tok = base64.b64encode(f"{SPLUNK_USER}:{SPLUNK_PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {tok}"}


def ensure_index(retries=60):
    url = f"{MGMT_URL}/services/data/indexes"
    ctx = _ssl_ctx()
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, data=f"name={INDEX}".encode(), headers=_auth_header())
            urllib.request.urlopen(req, timeout=8, context=ctx).read()
            print(f"[forge] índice '{INDEX}' creado.", flush=True)
            return
        except urllib.error.HTTPError as e:
            if e.code == 409:
                print(f"[forge] índice '{INDEX}' ya existe.", flush=True)
                return
            time.sleep(3)
        except Exception:
            time.sleep(3)
    raise SystemExit("[forge] no pude crear el índice (splunkd no respondió)")


def wait_for_hec(retries=60):
    health = HEC_URL.replace("/services/collector/event", "/services/collector/health")
    ctx = _ssl_ctx()
    for _ in range(retries):
        try:
            urllib.request.urlopen(urllib.request.Request(health), timeout=4, context=ctx)
            return
        except urllib.error.HTTPError as e:
            if e.code in (200, 400):
                return
            time.sleep(3)
        except Exception:
            time.sleep(3)
    raise SystemExit("[forge] HEC no respondió a tiempo")


def ship(batch):
    body = "\n".join(json.dumps(e) for e in batch).encode()
    req = urllib.request.Request(
        HEC_URL, data=body,
        headers={"Authorization": f"Splunk {HEC_TOKEN}", "Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=20, context=_ssl_ctx()).read()


def main():
    print(f"[forge] generando dataset de autenticación (seed={SEED}) ...", flush=True)
    forge_benign()
    forge_attack()
    events.sort(key=lambda e: e["time"])
    print(f"[forge] {len(events)} eventos generados. Preparando Splunk...", flush=True)
    ensure_index()
    wait_for_hec()
    print("[forge] HEC listo. Ingestando...", flush=True)
    for i in range(0, len(events), 200):
        ship(events[i:i + 200])
    print(f"[forge] ingesta completada: {len(events)} eventos en index={INDEX}.", flush=True)
    with open("/tmp/forge_done", "w") as fh:
        fh.write(str(len(events)))


if __name__ == "__main__":
    main()

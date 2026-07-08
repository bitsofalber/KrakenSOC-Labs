#!/usr/bin/env python3
"""
Data-forge de Cryptolock — genera la telemetría de un brote de ransomware en la
flota Windows de Northwind y la ingesta en Splunk vía HEC (índice 'northwind').

Escenario: un ransomware (cryptolock.exe) detona en un endpoint, borra las
shadow copies, inhibe la recuperación de Windows, para el antivirus, cifra
masivamente los ficheros (extensión .cryptolock) y deja notas de rescate. El
alumno reconstruye el brote con SPL y decodifica un comando ofuscado para la
flag.

Fuentes: Sysmon EventID=1 (creación de proceso) y EventID=11 (creación de
fichero: ficheros cifrados y notas de rescate).

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
SEED = int(os.environ.get("FORGE_SEED", "1486"))
MGMT_URL = os.environ.get("SPLUNK_MGMT_URL", "https://splunk:8089")
SPLUNK_USER = os.environ.get("SPLUNK_USER", "admin")
SPLUNK_PASSWORD = os.environ.get("SPLUNK_PASSWORD", "Changeme123!")


def _load_flag():
    v = os.environ.get("CRYPTOLOCK_FLAG")
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
PATIENT_ZERO = "NW-WKS-018"
USER = "m.suyama"
RANSOM = r"C:\Users\m.suyama\AppData\Local\Temp\cryptolock.exe"
RANSOM_EXT = ".cryptolock"
RANSOM_NOTE = "HOW_TO_DECRYPT.html"
ENCRYPTED_COUNT = 45
PS = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

T0 = time.time() - 3600
events = []
USERS = ["nancy.davolio", "a.fuller", "j.leverling", "m.peacock", "m.suyama", "r.king"]
FLEET = [f"NW-WKS-{i:03d}" for i in range(1, 40)]


def b64(s):
    return base64.b64encode(s.encode()).decode()


def add(ts, fields):
    events.append({
        "time": round(ts, 3),
        "host": fields.get("Computer", "NW-WKS"),
        "source": "northwind:forge",
        "sourcetype": "Sysmon",
        "index": INDEX,
        "event": fields,
    })


def proc(ts, host, user, image, cmd, parent, technique="", event_type=""):
    add(ts, {
        "EventID": 1, "Computer": host, "User": f"{DOMAIN}\\{user}",
        "Image": image, "CommandLine": cmd,
        "ParentImage": parent if "\\" in parent else rf"C:\Windows\System32\{parent}",
        "ProcessId": rng.randint(2000, 9000),
        "mitre_technique": technique, "event_type": event_type,
    })


def filecreate(ts, host, user, target, event_type=""):
    add(ts, {
        "EventID": 11, "Computer": host, "User": f"{DOMAIN}\\{user}",
        "Image": RANSOM, "TargetFilename": target, "event_type": event_type,
    })


# ── Ruido benigno ────────────────────────────────────────────────────────────
BENIGN_PROCS = [
    (r"C:\Windows\System32\svchost.exe", "svchost.exe -k netsvcs"),
    (r"C:\Program Files\Google\Chrome\chrome.exe", "chrome.exe"),
    (r"C:\Windows\explorer.exe", "explorer.exe"),
    (r"C:\Windows\System32\backup.exe", "backup.exe /daily"),
]


def forge_benign():
    for _ in range(80):
        img, cmd = rng.choice(BENIGN_PROCS)
        proc(T0 + rng.uniform(0, 3300), rng.choice(FLEET), rng.choice(USERS),
             img, cmd, "services.exe", "T1059.001", "Benign")
    # creación de ficheros normales (documentos de trabajo)
    for _ in range(40):
        h = rng.choice(FLEET)
        filecreate(T0 + rng.uniform(0, 3300), h, rng.choice(USERS),
                   rf"C:\Users\{rng.choice(USERS)}\Documents\report_{rng.randint(1,99)}.docx", "Benign")


# ── Brote de ransomware (secuencia determinista) ─────────────────────────────
def forge_ransomware():
    t = T0 + 400
    # 1) El binario del ransomware se ejecuta (lanzado por una macro de Office)
    proc(t, PATIENT_ZERO, USER, RANSOM, f"\"{RANSOM}\" /enc",
         r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
         "T1204.002", "Ransomware Launch")

    # 2) Borra shadow copies e inhibe la recuperación — T1490
    for cmd, img, tech in [
        ("vssadmin.exe delete shadows /all /quiet", r"C:\Windows\System32\vssadmin.exe", "T1490"),
        ("wmic.exe shadowcopy delete", r"C:\Windows\System32\wbem\WMIC.exe", "T1490"),
        ("bcdedit.exe /set {default} recoveryenabled no", r"C:\Windows\System32\bcdedit.exe", "T1490"),
        ("bcdedit.exe /set {default} bootstatuspolicy ignoreallfailures", r"C:\Windows\System32\bcdedit.exe", "T1490"),
        ("wbadmin.exe delete catalog -quiet", r"C:\Windows\System32\wbadmin.exe", "T1490"),
    ]:
        t += 8
        proc(t, PATIENT_ZERO, USER, img, cmd, RANSOM, tech, "Inhibit Recovery")

    # 3) Para el antivirus y servicios — T1489 / T1562.001
    for cmd, img, tech in [
        ("taskkill.exe /IM MsMpEng.exe /F", r"C:\Windows\System32\taskkill.exe", "T1562.001"),
        ("net.exe stop \"Windows Defender Antivirus Service\" /y", r"C:\Windows\System32\net.exe", "T1489"),
        ("sc.exe stop SQLTELEMETRY", r"C:\Windows\System32\sc.exe", "T1489"),
    ]:
        t += 8
        proc(t, PATIENT_ZERO, USER, img, cmd, RANSOM, tech, "Service Stop")

    # 4) Cifrado masivo de ficheros — T1486
    dirs = ["Documents", "Desktop", "Downloads", "Pictures"]
    exts = ["docx", "xlsx", "pdf", "jpg", "pptx"]
    for i in range(ENCRYPTED_COUNT):
        t += 0.3
        d = rng.choice(dirs)
        name = f"file_{i:03d}.{rng.choice(exts)}{RANSOM_EXT}"
        filecreate(t, PATIENT_ZERO, USER,
                   rf"C:\Users\{USER}\{d}\{name}", "File Encrypted")
    # notas de rescate en varios directorios
    for d in dirs:
        t += 0.5
        filecreate(t, PATIENT_ZERO, USER, rf"C:\Users\{USER}\{d}\{RANSOM_NOTE}", "Ransom Note")

    # 5) Comando ofuscado con la FLAG (el ransomware baliza/deja marca)
    flag_script = f"$id='cryptolock';Write-Output '{FLAG}'"
    t += 5
    proc(t, PATIENT_ZERO, USER, PS,
         f"powershell.exe -NoProfile -EncodedCommand {b64(flag_script)}",
         RANSOM, "T1027", "Encoded Command")


# ── Ingesta HEC (mismo patrón que los otros labs de Splunk) ──────────────────
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
    print(f"[forge] generando dataset de ransomware (seed={SEED}) ...", flush=True)
    forge_benign()
    forge_ransomware()
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

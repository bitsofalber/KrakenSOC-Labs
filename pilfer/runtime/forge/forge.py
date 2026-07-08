#!/usr/bin/env python3
"""
Data-forge de Pilfer — genera la telemetría de un robo de datos por un insider
(empleado saliente) que copia ficheros sensibles a un USB, y la ingesta en
Splunk vía HEC (índice 'northwind').

Escenario: r.king, un comercial que deja la empresa, conecta una unidad USB,
accede a ficheros sensibles (nóminas, cartera de clientes) y los copia a la
unidad extraíble tras comprimirlos. No hay malware: es una amenaza interna. El
alumno lo reconstruye con SPL y decodifica un comando ofuscado para la flag.

Fuentes: WinEventLog:Security (6416 dispositivo externo reconocido, 4663 acceso
a fichero) y Sysmon (EventID 1 proceso, EventID 11 creación de fichero en la unidad E:).

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
SEED = int(os.environ.get("FORGE_SEED", "1052"))
MGMT_URL = os.environ.get("SPLUNK_MGMT_URL", "https://splunk:8089")
SPLUNK_USER = os.environ.get("SPLUNK_USER", "admin")
SPLUNK_PASSWORD = os.environ.get("SPLUNK_PASSWORD", "Changeme123!")


def _load_flag():
    v = os.environ.get("PILFER_FLAG")
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
INSIDER = "r.king"                 # el empleado saliente
HOST = "NW-WKS-020"                # su estación
USB_DRIVE = "E:"                   # unidad extraíble
USB_DEVICE = "USBSTOR\\Disk&Ven_SanDisk&Prod_Ultra&Rev_1.00"
PS = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

# Ficheros sensibles robados (el más sensible: las nóminas)
STOLEN = [
    ("payroll_Q3.csv", r"C:\Finance\HR"),
    ("customer_master.xlsx", r"C:\Sales\CRM"),
    ("pricing_2026.xlsx", r"C:\Sales"),
    ("contracts_key_accounts.zip", r"C:\Sales\Legal"),
    ("salaries_all.xlsx", r"C:\Finance\HR"),
    ("supplier_contacts.csv", r"C:\Procurement"),
    ("product_roadmap.pptx", r"C:\Strategy"),
    ("employee_directory.csv", r"C:\HR"),
]

T0 = time.time() - 3600
events = []
USERS = ["nancy.davolio", "a.fuller", "j.leverling", "m.peacock", "r.king", "l.callahan"]
FLEET = [f"NW-WKS-{i:03d}" for i in range(1, 40)]


def b64(s):
    return base64.b64encode(s.encode()).decode()


def add(sourcetype, ts, fields):
    events.append({
        "time": round(ts, 3),
        "host": fields.get("Computer", "NW-WKS"),
        "source": "northwind:forge",
        "sourcetype": sourcetype,
        "index": INDEX,
        "event": fields,
    })


def proc(ts, host, user, image, cmd, parent, technique="", event_type=""):
    add("Sysmon", ts, {
        "EventID": 1, "Computer": host, "User": f"{DOMAIN}\\{user}",
        "Image": image, "CommandLine": cmd,
        "ParentImage": parent if "\\" in parent else rf"C:\Windows\System32\{parent}",
        "ProcessId": rng.randint(2000, 9000),
        "mitre_technique": technique, "event_type": event_type,
    })


def filecreate(ts, host, user, target, event_type=""):
    add("Sysmon", ts, {
        "EventID": 11, "Computer": host, "User": f"{DOMAIN}\\{user}",
        "Image": r"C:\Windows\explorer.exe", "TargetFilename": target,
        "event_type": event_type,
    })


# ── Ruido benigno ────────────────────────────────────────────────────────────
def forge_benign():
    for _ in range(70):
        proc(T0 + rng.uniform(0, 3300), rng.choice(FLEET), rng.choice(USERS),
             r"C:\Windows\explorer.exe", "explorer.exe", "userinit.exe", "T1059.001", "Benign")
    for _ in range(40):
        u = rng.choice(USERS)
        filecreate(T0 + rng.uniform(0, 3300), rng.choice(FLEET), u,
                   rf"C:\Users\{u}\Documents\notes_{rng.randint(1,99)}.txt", "Benign")
    # algún USB benigno en otro host (falso positivo típico)
    add("WinEventLog:Security", T0 + rng.uniform(0, 3300), {
        "EventCode": 6416, "Computer": "NW-WKS-005", "Account_Name": "a.fuller",
        "Device_Description": "Generic USB Keyboard",
        "signature": "A new external device was recognized by the system",
    })


# ── Robo por el insider (secuencia determinista) ─────────────────────────────
def forge_theft():
    t = T0 + 400
    # 1) Conecta el USB — WinEventLog:Security 6416
    add("WinEventLog:Security", t, {
        "EventCode": 6416, "Computer": HOST, "Account_Name": INSIDER,
        "Device_Description": "SanDisk Ultra USB Device", "Device_ID": USB_DEVICE,
        "signature": "A new external device was recognized by the system",
    })

    # 2) Accede (lee) los ficheros sensibles — WinEventLog:Security 4663
    for i, (name, path) in enumerate(STOLEN):
        add("WinEventLog:Security", t + 20 + i * 4, {
            "EventCode": 4663, "Computer": HOST, "Account_Name": INSIDER,
            "Object_Name": rf"{path}\{name}", "Accesses": "ReadData (or ListDirectory)",
            "signature": "An attempt was made to access an object",
        })

    # 3) Comprime los datos para estacionarlos — T1074.001 (Local Data Staging)
    t += 20 + len(STOLEN) * 4 + 10
    proc(t, HOST, INSIDER, PS,
         "powershell.exe Compress-Archive -Path C:\\Finance\\HR\\*,C:\\Sales\\CRM\\* -DestinationPath C:\\Users\\r.king\\Desktop\\backup.zip",
         "explorer.exe", "T1074.001", "Data Staging")

    # 4) Copia los ficheros a la unidad USB — Sysmon 11 en E:\  (T1052.001)
    for i, (name, _path) in enumerate(STOLEN):
        filecreate(t + 15 + i * 3, HOST, INSIDER, rf"{USB_DRIVE}\{name}", "USB File Copy")
    filecreate(t + 15 + len(STOLEN) * 3, HOST, INSIDER, rf"{USB_DRIVE}\backup.zip", "USB File Copy")

    # 5) Comando ofuscado con la FLAG (el insider borra su rastro / deja marca)
    flag_script = f"$who='insider';Write-Output '{FLAG}'"
    proc(t + 60, HOST, INSIDER, PS,
         f"powershell.exe -NoProfile -EncodedCommand {b64(flag_script)}",
         "explorer.exe", "T1027", "Encoded Command")


# ── Ingesta HEC ──────────────────────────────────────────────────────────────
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
    print(f"[forge] generando dataset de insider/USB (seed={SEED}) ...", flush=True)
    forge_benign()
    forge_theft()
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

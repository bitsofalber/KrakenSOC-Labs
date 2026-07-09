#!/usr/bin/env python3
"""
Data-forge de Nimbus — genera un dataset CLOUD multi-fuente, determinista y
coherente, y lo ingesta en Splunk vía HEC (índice 'northwind').

El dataset cuenta UNA campaña de intrusión completa contra la nueva
infraestructura AWS de Northwind Global Systems ("Northwind se muda a la nube").
La cadena reconcilia la matriz Cloud de ATT&CK:

  - Acceso inicial   (T1078.004)  -> clave IAM filtrada de m.suarez usada desde
                                      una IP foránea + sign-in de riesgo (Azure AD)
  - Descubrimiento   (T1526/T1580) -> ráfaga de Describe*/List* (enumeración)
  - Credential Access(T1552.005)  -> SSRF a la IMDS (169.254.169.254) roba el rol
  - Persistencia     (T1098.001)  -> CreateAccessKey (clave adicional) + Lambda
  - Defense Evasion  (T1562.008)  -> StopLogging / DeleteTrail (cegar CloudTrail)
  - Collection       (T1530)      -> bucket S3 de RRHH hecho público + GetObject
  - Exfiltration     (T1537)      -> PutBucketPolicy comparte datos a una cuenta
                                      AWS externa controlada por el atacante

Todo es SINTÉTICO (no hay datos reales) y REPRODUCIBLE (seed fija) para que las
respuestas del cuestionario sean estables. Se genera ruido benigno para que la
actividad maliciosa haya que buscarla de verdad con SPL.

La flag va incrustada en una variable de entorno de una Lambda que el atacante
crea para persistir: un blob base64 que decodifica a la flag. En el repo,
NIMBUS_FLAG es un DECOY; el valor real se inyecta en CI desde un secret.
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
    # NIMBUS_FLAG solo se usa para pruebas de mantenedor.
    v = os.environ.get("NIMBUS_FLAG")
    if v:
        return v.strip()
    try:
        with open("/seed/flag.txt", "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{th15_15_n0t_th3_r34l_fl4g}"


FLAG = _load_flag()

# ─── Canon (IOCs de la campaña cloud) ────────────────────────────────────────
ACCOUNT = "409915291301"                 # cuenta AWS de producción de Northwind
EXT_ACCOUNT = "600377889922"             # cuenta AWS externa del atacante (exfil)
REGION = "eu-west-1"
USER = "m.suarez"                        # dev con clave IAM filtrada
USER_ARN = f"arn:aws:iam::{ACCOUNT}:user/{USER}"
UPN = "m.suarez@northwind-systems.com"
LEAKED_KEY = "AKIA4NWDEVMSUAREZ01"       # clave comprometida (acceso inicial)
BACKDOOR_KEY = "AKIA4NWPERSIST9931X"     # clave que el atacante crea (persistencia)
ATTACKER_IP = "203.0.113.77"             # IP foránea del atacante
WEB_INSTANCE = "i-0f3c9a1b2cnwweb01"     # instancia web vulnerable a SSRF
WEB_ROLE = "northwind-web-role"          # rol robado vía IMDS
IMDS_IP = "169.254.169.254"             # endpoint de metadatos de la instancia
TRAIL = "northwind-org-trail"            # el CloudTrail que el atacante apaga
HR_BUCKET = "northwind-hr-exports"       # bucket S3 con datos sensibles
HR_OBJECT = "payroll_Q3_2026.csv"        # fichero robado
LAMBDA_NAME = "nw-metrics-sync"          # Lambda de persistencia (esconde la flag)
ENUM_COUNT = 45                          # nº exacto de llamadas de enumeración

random.seed(SEED)
rng = random.Random(SEED)

# Ventana temporal: la campaña ocurrió en la última hora (para "Last 24h").
T0 = time.time() - 3600
events = []


def add(sourcetype, ts, fields, source="northwind:cloud"):
    events.append({
        "time": round(ts, 3),
        "host": "cloudtrail" if sourcetype.startswith("aws") else "azure",
        "source": source,
        "sourcetype": sourcetype,
        "index": INDEX,
        "event": fields,
    })


def b64(s):
    return base64.b64encode(s.encode()).decode()


def ct(ts, event_name, source, ip, identity, params=None, error=None, extra=None):
    """Construye un evento CloudTrail (aws:cloudtrail) con forma realista."""
    ev = {
        "eventTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
        "eventSource": source,
        "eventName": event_name,
        "awsRegion": REGION,
        "sourceIPAddress": ip,
        "userIdentity": identity,
        "recipientAccountId": ACCOUNT,
        "readOnly": event_name.startswith(("Describe", "List", "Get", "Lookup")),
    }
    if params is not None:
        ev["requestParameters"] = params
    if error is not None:
        ev["errorCode"] = error
    if extra:
        ev.update(extra)
    add("aws:cloudtrail", ts, ev)


def iam_user(name=USER, key=LEAKED_KEY, ip_type="IAMUser"):
    return {
        "type": ip_type,
        "userName": name,
        "arn": f"arn:aws:iam::{ACCOUNT}:user/{name}",
        "accountId": ACCOUNT,
        "accessKeyId": key,
    }


def assumed_role(role=WEB_ROLE, key="ASIA4NWROLESTOLEN01"):
    return {
        "type": "AssumedRole",
        "arn": f"arn:aws:sts::{ACCOUNT}:assumed-role/{role}/i-web",
        "accountId": ACCOUNT,
        "accessKeyId": key,
        "sessionContext": {"sessionIssuer": {"userName": role}},
    }


# ─── Ruido benigno de fondo ──────────────────────────────────────────────────
BENIGN_USERS = ["a.fuller", "j.leverling", "m.peacock", "l.callahan", "r.king"]
BENIGN_ROLES = ["northwind-ci-deploy", "northwind-backup-role", "AWSServiceRoleForAutoScaling"]
CORP_IPS = ["88.24.10.5", "88.24.10.6", "88.24.11.14", "88.24.12.30"]
BENIGN_READ = ["DescribeInstances", "ListBuckets", "GetCallerIdentity",
               "DescribeVolumes", "ListFunctions", "DescribeSecurityGroups"]
BENIGN_WRITE = ["PutObject", "RunInstances", "CreateTags", "UpdateFunctionCode"]
BENIGN_DOMAINS = ["www.microsoft.com", "outlook.office365.com", "clients.google.com",
                  "cdn.jsdelivr.net", "api.github.com", "s3.eu-west-1.amazonaws.com"]


def forge_noise():
    # CloudTrail benigno: operaciones normales de la flota y del CI, desde IPs corp.
    for _ in range(260):
        ts = T0 + rng.uniform(0, 3300)
        if rng.random() < 0.55:
            ev, src = rng.choice(BENIGN_READ), "ec2.amazonaws.com"
            ident = iam_user(rng.choice(BENIGN_USERS),
                             key=f"AKIA4NW{rng.randint(1000,9999)}OPS",
                             ip_type="IAMUser")
        else:
            ev, src = rng.choice(BENIGN_WRITE), "s3.amazonaws.com"
            ident = assumed_role(rng.choice(BENIGN_ROLES),
                                 key=f"ASIA4NW{rng.randint(1000,9999)}CI")
        ct(ts, ev, src, rng.choice(CORP_IPS), ident)
    # ConsoleLogin benignos correctos
    for _ in range(30):
        ts = T0 + rng.uniform(0, 3300)
        u = rng.choice(BENIGN_USERS)
        ct(ts, "ConsoleLogin", "signin.amazonaws.com", rng.choice(CORP_IPS),
           iam_user(u, key="-", ip_type="IAMUser"),
           extra={"responseElements": {"ConsoleLogin": "Success"}})
    # Sign-ins Azure AD benignos (Madrid)
    for _ in range(70):
        ts = T0 + rng.uniform(0, 3300)
        u = rng.choice(BENIGN_USERS)
        add("azure:signin", ts, {
            "userPrincipalName": f"{u}@northwind-systems.com",
            "ipAddress": f"88.24.{rng.randint(1,40)}.{rng.randint(1,254)}",
            "location": "Madrid, ES", "status": "success",
            "appDisplayName": "AWS Single Sign-On", "riskLevelDuringSignIn": "none",
        })
    # Proxy web benigno de las instancias
    for _ in range(150):
        ts = T0 + rng.uniform(0, 3300)
        d = rng.choice(BENIGN_DOMAINS)
        add("proxy:web", ts, {
            "src_instance": WEB_INSTANCE,
            "src_ip": f"10.20.{rng.randint(1,8)}.{rng.randint(2,254)}",
            "dest_ip": f"52.{rng.randint(1,60)}.{rng.randint(1,254)}.{rng.randint(1,254)}",
            "dest_host": d, "uri": "/", "http_method": "GET", "status": 200,
        })
    # Accesos S3 benignos (usuarios autorizados)
    for _ in range(40):
        ts = T0 + rng.uniform(0, 3300)
        add("aws:s3:serveraccess", ts, {
            "bucket": rng.choice(["northwind-app-assets", "northwind-logs-archive"]),
            "key": f"data/file_{rng.randint(1,999)}.dat",
            "operation": "REST.GET.OBJECT",
            "requester": rng.choice(BENIGN_USERS), "remote_ip": rng.choice(CORP_IPS),
            "http_status": 200,
        })


# ─── Cadena de ataque (los eventos que el alumno debe encontrar) ─────────────
def forge_attack():
    t = T0 + 300  # la intrusión arranca a los 5 min de la ventana

    # ── Act 1 · Acceso inicial (T1078.004)
    # Sign-in de riesgo en Azure AD (SSO hacia AWS) desde la IP del atacante.
    add("azure:signin", t, {
        "userPrincipalName": UPN, "ipAddress": ATTACKER_IP,
        "location": "Unknown", "status": "success",
        "appDisplayName": "AWS Single Sign-On", "riskLevelDuringSignIn": "high",
        "note": "Impossible-travel vs prior Madrid sign-in",
    })
    # La clave IAM filtrada se usa desde la misma IP foránea (GetCallerIdentity).
    ct(t + 25, "GetCallerIdentity", "sts.amazonaws.com", ATTACKER_IP,
       iam_user(USER, LEAKED_KEY))
    # ConsoleLogin adicional desde la IP del atacante (corrobora el acceso).
    ct(t + 40, "ConsoleLogin", "signin.amazonaws.com", ATTACKER_IP,
       iam_user(USER, "-"), extra={"responseElements": {"ConsoleLogin": "Success"},
                                   "additionalEventData": {"MFAUsed": "No"}})

    # ── Act 2 · Descubrimiento / enumeración (T1526 + T1580)
    # Ráfaga de ENUM_COUNT llamadas Describe*/List*/Get* en pocos minutos.
    enum_apis = [
        ("DescribeInstances", "ec2.amazonaws.com"), ("DescribeSecurityGroups", "ec2.amazonaws.com"),
        ("DescribeVolumes", "ec2.amazonaws.com"), ("DescribeSnapshots", "ec2.amazonaws.com"),
        ("ListBuckets", "s3.amazonaws.com"), ("ListUsers", "iam.amazonaws.com"),
        ("ListRoles", "iam.amazonaws.com"), ("ListAccessKeys", "iam.amazonaws.com"),
        ("ListFunctions", "lambda.amazonaws.com"), ("DescribeDBInstances", "rds.amazonaws.com"),
        ("ListInstanceProfiles", "iam.amazonaws.com"), ("ListSecrets", "secretsmanager.amazonaws.com"),
    ]
    # Nota: todas Describe*/List* -> la SPL canónica (eventName=Describe* OR
    # eventName=List*) desde la IP del atacante cuenta EXACTAMENTE ENUM_COUNT.
    et = t + 120
    for i in range(ENUM_COUNT):
        name, src = enum_apis[i % len(enum_apis)]
        ct(et + i * 4, name, src, ATTACKER_IP, iam_user(USER, LEAKED_KEY))

    # ── Act 3 · Credential Access vía SSRF a la IMDS (T1552.005)
    # La app web es vulnerable a SSRF: el atacante la usa para leer las
    # credenciales temporales del rol de la instancia en 169.254.169.254.
    st = et + ENUM_COUNT * 4 + 30
    add("proxy:web", st, {
        "src_instance": WEB_INSTANCE, "src_ip": "10.20.3.41",
        "dest_ip": IMDS_IP, "dest_host": "instance-data",
        "uri": f"/latest/meta-data/iam/security-credentials/{WEB_ROLE}",
        "http_method": "GET", "status": 200, "bytes": 1108,
        "note": "SSRF desde parametro url= del endpoint /fetch",
    })
    # Con el rol robado, el atacante ya opera como AssumedRole.
    ct(st + 20, "GetCallerIdentity", "sts.amazonaws.com", ATTACKER_IP, assumed_role())

    # ── Act 4 · Defense Evasion: apagar CloudTrail (T1562.008)
    dt = st + 60
    ct(dt, "StopLogging", "cloudtrail.amazonaws.com", ATTACKER_IP,
       iam_user(USER, LEAKED_KEY),
       params={"name": f"arn:aws:cloudtrail:{REGION}:{ACCOUNT}:trail/{TRAIL}"})
    ct(dt + 15, "DeleteTrail", "cloudtrail.amazonaws.com", ATTACKER_IP,
       iam_user(USER, LEAKED_KEY),
       params={"name": f"arn:aws:cloudtrail:{REGION}:{ACCOUNT}:trail/{TRAIL}"},
       error="AccessDenied")   # lo intenta borrar pero solo consigue pararlo

    # ── Act 5 · Persistencia (T1098.001) + Lambda con la flag
    pt = dt + 60
    # Clave IAM adicional para persistir el acceso.
    ct(pt, "CreateAccessKey", "iam.amazonaws.com", ATTACKER_IP,
       iam_user(USER, LEAKED_KEY),
       params={"userName": USER},
       extra={"responseElements": {"accessKey": {
           "userName": USER, "accessKeyId": BACKDOOR_KEY, "status": "Active"}}})
    # Lambda de "métricas" como backdoor; su env var NOTE esconde la flag (base64).
    ct(pt + 25, "CreateFunction20150331", "lambda.amazonaws.com", ATTACKER_IP,
       iam_user(USER, LEAKED_KEY),
       params={
           "functionName": LAMBDA_NAME, "runtime": "python3.12",
           "handler": "index.handler", "role": f"arn:aws:iam::{ACCOUNT}:role/{WEB_ROLE}",
           "environment": {"variables": {
               "REGION": REGION,
               "NOTE": b64("operator-note flag=" + FLAG),
           }},
       })

    # ── Act 6 · Collection: exponer y leer el bucket de RRHH (T1530)
    gt = pt + 60
    # Hacer público el bucket (policy con Principal:*).
    ct(gt, "PutBucketPolicy", "s3.amazonaws.com", ATTACKER_IP, assumed_role(),
       params={"bucketName": HR_BUCKET,
               "bucketPolicy": {"Statement": [{"Effect": "Allow", "Principal": "*",
                                               "Action": "s3:GetObject",
                                               "Resource": f"arn:aws:s3:::{HR_BUCKET}/*"}]}})
    # Leer el fichero sensible (GetObject en el server access log).
    add("aws:s3:serveraccess", gt + 20, {
        "bucket": HR_BUCKET, "key": HR_OBJECT, "operation": "REST.GET.OBJECT",
        "requester": "anonymous", "remote_ip": ATTACKER_IP, "http_status": 200,
        "bytes_sent": 284471,
    })

    # ── Act 7 · Exfiltración a una cuenta AWS externa (T1537)
    xt = gt + 60
    # Comparte una snapshot de la BD y el bucket con la cuenta del atacante.
    ct(xt, "ModifySnapshotAttribute", "ec2.amazonaws.com", ATTACKER_IP, assumed_role(),
       params={"snapshotId": "snap-0nwprod9db31",
               "createVolumePermission": {"add": [{"userId": EXT_ACCOUNT}]}})
    ct(xt + 20, "PutBucketPolicy", "s3.amazonaws.com", ATTACKER_IP, assumed_role(),
       params={"bucketName": HR_BUCKET,
               "bucketPolicy": {"Statement": [{"Effect": "Allow",
                                               "Principal": {"AWS": f"arn:aws:iam::{EXT_ACCOUNT}:root"},
                                               "Action": "s3:*",
                                               "Resource": f"arn:aws:s3:::{HR_BUCKET}/*"}]}})


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
            if e.code in (200, 400):
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
    """Crea el índice vía REST (idempotente)."""
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
            if e.code == 409:
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
    print(f"[forge] generando dataset cloud (seed={SEED}) ...", flush=True)
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
    with open("/tmp/forge_done", "w") as fh:
        fh.write(str(len(events)))


if __name__ == "__main__":
    main()

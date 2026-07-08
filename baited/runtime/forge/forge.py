#!/usr/bin/env python3
"""
Data-forge de Baited — genera logs de un gateway de correo (benignos y de
phishing) y los ingesta en Splunk vía HEC (índice 'northwind').

Escenario: una campaña de phishing golpea a Northwind Global Systems. Dominios
remitentes typosquat que suplantan a Microsoft y a la propia Northwind, con
fallos de SPF/DKIM/DMARC, URLs de credential harvesting por HTTP y adjuntos
peligrosos. Casi todos se bloquean o van a cuarentena — pero UNO se ENTREGA: el
que compromete a s.buchanan (el acceso inicial que da pie a los otros labs del
canon). El alumno investiga con SPL, puntúa el phishing y decodifica el token de
la URL maliciosa para recuperar la flag.

Fuente: sourcetype=email:gateway (un evento por correo, JSON).

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
SEED = int(os.environ.get("FORGE_SEED", "1566"))
MGMT_URL = os.environ.get("SPLUNK_MGMT_URL", "https://splunk:8089")
SPLUNK_USER = os.environ.get("SPLUNK_USER", "admin")
SPLUNK_PASSWORD = os.environ.get("SPLUNK_PASSWORD", "Changeme123!")


def _load_flag():
    v = os.environ.get("BAITED_FLAG")
    if v:
        return v.strip()
    try:
        with open("/seed/flag.txt", "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NORTHWIND{th15_15_n0t_th3_r34l_fl4g}"


FLAG = _load_flag()
rng = random.Random(SEED)

CAMPAIGN_IP = "45.83.220.60"                 # IP del atacante (la campaña)
VICTIM = "s.buchanan@northwind-systems.com"  # el que cae (canon)
TYPO_NORTHWIND = "northw1nd-systems.com"      # typosquat de northwind (1 por i)
FLAG_TOKEN = base64.b64encode(FLAG.encode()).decode()

T0 = time.time() - 3600
events = []

RECIPIENTS = [f"{u}@northwind-systems.com" for u in
              ["nancy.davolio", "a.fuller", "j.leverling", "m.peacock",
               "m.suyama", "r.king", "l.callahan", "s.buchanan"]]


def add(ts, fields):
    events.append({
        "time": round(ts, 3),
        "host": "NW-MAILGW01",
        "source": "northwind:forge",
        "sourcetype": "email:gateway",
        "index": INDEX,
        "event": fields,
    })


def mail(ts, sender, domain, recipient, subject, url, att, att_hash,
         src, spf, dkim, dmarc, action):
    add(ts, {
        "sender_email": sender, "sender_domain": domain, "recipient": recipient,
        "subject": subject, "url": url, "attachment_name": att,
        "attachment_hash": att_hash, "source_ip": src,
        "spf_result": spf, "dkim_result": dkim, "dmarc_result": dmarc,
        "action": action,
    })


# ── Correo benigno legítimo (auth OK, HTTPS, entregado) ──────────────────────
BENIGN = [
    ("newsletter@northwind-systems.com", "northwind-systems.com", "Weekly company update", "https://northwind-systems.com/news", "NA", "NA"),
    ("no-reply@microsoft.com", "microsoft.com", "Your Microsoft 365 receipt", "https://microsoft.com/billing", "NA", "NA"),
    ("hr@northwind-systems.com", "northwind-systems.com", "Q3 benefits enrollment", "https://hr.northwind-systems.com", "benefits.pdf", "3b5d5c3712955042212316173ccf37be"),
    ("no-reply@github.com", "github.com", "New sign-in to your account", "https://github.com/settings", "NA", "NA"),
    ("it-support@northwind-systems.com", "northwind-systems.com", "Scheduled maintenance window", "https://intranet.northwind-systems.com/it", "NA", "NA"),
    ("billing@aws.amazon.com", "amazon.com", "AWS invoice available", "https://aws.amazon.com/billing", "invoice.pdf", "1a79a4d60de6718e8e5b326e338ae533"),
]


def forge_benign():
    for i, (sender, dom, subj, url, att, h) in enumerate(BENIGN):
        add(T0 + rng.uniform(0, 3300), {
            "sender_email": sender, "sender_domain": dom,
            "recipient": rng.choice(RECIPIENTS), "subject": subj, "url": url,
            "attachment_name": att, "attachment_hash": h,
            "source_ip": f"52.{rng.randint(1,60)}.{rng.randint(1,254)}.{rng.randint(1,254)}",
            "spf_result": "pass", "dkim_result": "pass", "dmarc_result": "pass",
            "action": "delivered",
        })
    # algún correo legítimo con un fallo aislado de DKIM (falso positivo típico)
    add(T0 + rng.uniform(0, 3300), {
        "sender_email": "events@partner-conf.com", "sender_domain": "partner-conf.com",
        "recipient": rng.choice(RECIPIENTS), "subject": "Conference invitation",
        "url": "https://partner-conf.com/register", "attachment_name": "NA",
        "attachment_hash": "NA", "source_ip": "198.51.100.7",
        "spf_result": "pass", "dkim_result": "fail", "dmarc_result": "pass",
        "action": "delivered",
    })


# ── Campaña de phishing (lista fija => recuentos deterministas) ──────────────
# (sender, domain, subject, url, attachment, hash, spf, dkim, dmarc, action)
MAL = [
    ("security-update@micr0soft-support.com", "micr0soft-support.com",
     "Password Reset Required", "http://micr0soft-support.com/reset",
     "reset.html", "44d88612fea8a8f36de82e1278abb02f",
     "fail", "fail", "fail", "quarantined"),
    ("payroll@nw-payroll.net", "nw-payroll.net",
     "Updated Salary Slip Q3", "http://nw-payroll.net/login",
     "salary_update.html", "e99a18c428cb38d5f260853678922e03",
     "fail", "fail", "fail", "blocked"),
    ("docs@docs-share-cdn.net", "docs-share-cdn.net",
     "You received a shared document", "http://docs-share-cdn.net/open",
     "invoice.docm", "202cb962ac59075b964b07152d234b70",
     "fail", "pass", "fail", "blocked"),
    ("hr-portal@northw1nd-systems.com", "northw1nd-systems.com",
     "Action required: benefits update", "http://northw1nd-systems.com/hr",
     "form.html", "e99a18c428cb38d5f260853678922e03",
     "fail", "fail", "fail", "quarantined"),
    ("no-reply@0ffice365-login.com", "0ffice365-login.com",
     "Your mailbox is almost full", "http://0ffice365-login.com/cleanup",
     "NA", "NA", "fail", "fail", "fail", "blocked"),
    ("support@amaz0n-billing.com", "amaz0n-billing.com",
     "Problem with your order", "http://amaz0n-billing.com/verify",
     "order.html", "44d88612fea8a8f36de82e1278abb02f",
     "fail", "fail", "fail", "quarantined"),
    ("alerts@dhl-tracking-cdn.net", "dhl-tracking-cdn.net",
     "Your parcel could not be delivered", "http://dhl-tracking-cdn.net/track",
     "label.html", "202cb962ac59075b964b07152d234b70",
     "fail", "pass", "fail", "blocked"),
]


def forge_phishing():
    t = T0 + 400
    for i, (sender, dom, subj, url, att, h, spf, dkim, dmarc, act) in enumerate(MAL):
        mail(t + i * 40, sender, dom, rng.choice(RECIPIENTS), subj, url, att, h,
             CAMPAIGN_IP, spf, dkim, dmarc, act)

    # ── El phish que SÍ se entrega y compromete a s.buchanan (con la FLAG en la URL)
    mail(t + len(MAL) * 40 + 60,
         "it-helpdesk@northw1nd-systems.com", TYPO_NORTHWIND, VICTIM,
         "Action required: verify your mailbox to avoid suspension",
         f"http://{TYPO_NORTHWIND}/verify?token={FLAG_TOKEN}",
         "mailbox_verify.html", "5d41402abc4b2a76b9719d911017c592",
         CAMPAIGN_IP, "fail", "fail", "fail", "delivered")


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
    print(f"[forge] generando dataset de phishing (seed={SEED}) ...", flush=True)
    forge_benign()
    forge_phishing()
    events.sort(key=lambda e: e["time"])
    print(f"[forge] {len(events)} correos generados. Preparando Splunk...", flush=True)
    ensure_index()
    wait_for_hec()
    print("[forge] HEC listo. Ingestando...", flush=True)
    for i in range(0, len(events), 200):
        ship(events[i:i + 200])
    print(f"[forge] ingesta completada: {len(events)} correos en index={INDEX}.", flush=True)
    with open("/tmp/forge_done", "w") as fh:
        fh.write(str(len(events)))


if __name__ == "__main__":
    main()

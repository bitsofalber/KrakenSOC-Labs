# Baited — Phishing Email Investigation

![difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![duration](https://img.shields.io/badge/duration-55m-blue)
![SFRS](https://img.shields.io/badge/SFRS-1.0.0-6f42c1)
![class](https://img.shields.io/badge/class-interactive-9cf)
![platform](https://img.shields.io/badge/platform-amd64%20only-orange)
![SIEM](https://img.shields.io/badge/SIEM-Splunk-black)

> Official KrakenSOC Runtime Lab (interactive class). SOCForge owns the questions, XP and progress; this runtime owns a **real Splunk** with the email-gateway logs already indexed.

## Overview
Baited spins up a **real Splunk** pre-loaded with a phishing campaign against Northwind. Typosquatted senders impersonate Microsoft and Northwind, emails fail SPF/DKIM/DMARC, carry credential-harvesting HTTP links and dangerous attachments. The gateway blocks or quarantines most of them — but **one gets through** to `s.buchanan`. You investigate with real **SPL**, score the phishing, and decode the malicious URL token to recover the flag. This is the **initial access** that starts the whole Northwind intrusion.

## Scenario
Northwind's mail gateway logs are in Splunk. A wave of phishing hit the company this morning. Find the phishing among the legitimate mail, identify the typosquat that slipped through, the employee who got it, the campaign's source IP and the malicious attachment — and recover the operator's flag hidden in the phishing link.

## Architecture
Two containers on an isolated network:
- **splunk** — Splunk Enterprise (official image), HEC enabled, index `northwind`.
- **forge** — a deterministic data-forge that generates the email dataset and ingests it via HEC, then idles.

```
forge ──HEC──▶ Splunk (index=northwind, sourcetype=email:gateway)  ◀── you (Splunk Web :8000, real SPL)
```

Everything is **synthetic** and **reproducible** (fixed seed) — the answers are stable.

## Learning Objectives
- Investigate a phishing campaign in a real SIEM with SPL.
- Use email authentication (SPF/DKIM/DMARC) to spot spoofing.
- Recognise typosquatted domains and credential-harvesting URLs.
- Build a phishing-score model and find the email that evaded the filters.
- Turn findings into detections (SPL / Sigma).

## Difficulty
`intermediate`

## Estimated Duration
~55 minutes

## MITRE ATT&CK
T1566 · T1566.001 · T1566.002 · T1078. See `mitre/navigator-layer.json`.

## Skills
SIEM · Splunk · SPL · Email Security · Phishing Investigation · Threat Hunting

## Requirements
- Docker + Docker Compose v2
- **≥ 4 GB RAM (6 GB recommended on Apple Silicon), ≥ 8 GB disk**
- A web browser for Splunk Web

## Compatibility — amd64 only
This lab is **amd64 (x86_64) only**: the official **Splunk container image is not published for ARM**.
- **Supported:** Intel/AMD (`linux/amd64`) — Splunk runs natively.
- **Best-effort (unsupported):** Apple Silicon / ARM runs it **under emulation** (slower boot, more RAM — give Docker ≥ 6 GB). `./doctor.sh` warns you.

## Quick Start
```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/baited
./deploy.sh
```
When it finishes, open **http://localhost:8000** (user `admin`, password from `.env`) and start with `index=northwind sourcetype=email:gateway`.

## Deployment
`./deploy.sh` checks the environment, pulls Splunk (Docker Hub) and the `forge` image (GHCR), brings both up, waits until Splunk is healthy and the dataset is ingested, and prints the Splunk URL + credentials.

> Maintainers who want to build the forge locally instead of pulling:
> `docker compose -f docker-compose.yml -f docker-compose.build.yml build`
> (local builds use a decoy flag; the real one is injected only in CI.)

## Validation
```bash
./verify.sh   # green when splunk is healthy and the forge has finished ingesting
```

## Lab Structure
Standard SFRS layout. The scenario generator lives in `runtime/forge/`; detection content in `rules/` (SPL + Sigma); indicators in `ioc/`, `timeline/`, `mitre/`.

## Evidence
All evidence is **inside Splunk**, in `index=northwind sourcetype=email:gateway`: sender, sender_domain, recipient, subject, url, attachment_name, attachment_hash, source_ip, spf/dkim/dmarc_result, action.

## Investigation Flow
1. `./deploy.sh`, then `./verify.sh`. Open Splunk Web (`:8000`).
2. Score the mail: SPF/DKIM/DMARC fails + http URL + dangerous attachment.
3. Find the phishing that was **delivered** despite failing auth — and who received it.
4. Identify the campaign's source IP, typosquat domain and malicious attachment hash.
5. Decode the base64 `token` in the malicious URL to recover the flag.
6. **Answer the questions inside KrakenSOC** to earn XP.

Starter searches:
```spl
index=northwind sourcetype=email:gateway (spf_result=fail OR dkim_result=fail OR dmarc_result=fail)
index=northwind sourcetype=email:gateway action=delivered dmarc_result=fail
index=northwind sourcetype=email:gateway url="http://*"
```

## Reset
```bash
./reset.sh    # fresh Splunk + re-ingest (a pristine index)
```

## Destroy
```bash
./destroy.sh  # remove containers, network and volumes
```

## Troubleshooting
- `./doctor.sh` reports Docker, architecture (amd64-only note), RAM, disk and port 8000.
- Port 8000 busy? Change `SPLUNK_WEB_PORT` in `.env`.
- Splunk slow to start on ARM is expected (emulation).

## FAQ
**Does Docker grade my answers?** No. Splunk is the investigation environment; the questions, flags and scoring live in KrakenSOC.
**Where's the solution?** Encrypted in `answers/` and unlocked from KrakenSOC (SFRS §8).
**Is the data real?** No — synthetic and deterministic, generated by `runtime/forge/`. No real PII.

## Credits
KrakenSOC / SOCForge. Scenario: Northwind Global Systems — the initial-access chapter. Content, dataset and code are original.

## License
MIT — see [`LICENSE`](./LICENSE).

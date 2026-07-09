# Nimbus — Northwind Goes to the Cloud

![difficulty](https://img.shields.io/badge/difficulty-advanced-red)
![duration](https://img.shields.io/badge/duration-90m-blue)
![SFRS](https://img.shields.io/badge/SFRS-1.0.0-6f42c1)
![class](https://img.shields.io/badge/class-interactive-9cf)
![platform](https://img.shields.io/badge/platform-amd64%20only-orange)
![SIEM](https://img.shields.io/badge/SIEM-Splunk-black)
![cloud](https://img.shields.io/badge/cloud-AWS%20CloudTrail-ff9900)

> Official KrakenSOC Runtime Lab (interactive class). SOCForge owns the questions, XP and progress; this runtime owns a **real Splunk** with the cloud campaign already indexed.

## Overview
Nimbus is the **cloud SIEM** lab of the Northwind universe. Northwind Global Systems has just moved to **AWS**, and an attacker got in. Docker spins up a **real Splunk** with a full **cloud** intrusion already indexed — **AWS CloudTrail**, **S3 access logs**, **Azure AD sign-ins** (SSO into AWS) and a **web proxy**. You open Splunk Web, write real **SPL**, and reconstruct the whole cloud kill chain, mapped to the **Cloud Matrix** of MITRE ATT&CK.

## Scenario
A high-risk "impossible travel" sign-in and a burst of API enumeration light up the SOC of **Northwind Global Systems**. Somewhere in an hour of cloud logs, a leaked IAM key, an SSRF that steals an instance role, a CloudTrail that goes dark, and data quietly shared to an outside AWS account are hiding in the noise. Your shift: reconstruct the cloud intrusion end to end and recover the operator's flag.

## Architecture
Two containers on an isolated network:
- **splunk** — Splunk Enterprise (official image) with HEC enabled and the `northwind` index.
- **forge** — a deterministic data-forge that generates the multi-source **cloud** dataset and ingests it via HEC, then idles.

```
forge ──HEC──▶ Splunk (index=northwind)  ◀── you (Splunk Web :8000, real SPL)
```

Everything is **synthetic** and **reproducible** (fixed seed) — the answers are stable. No real AWS account is touched and there is no real PII.

## Learning Objectives
- Investigate a real **cloud** intrusion in a real SIEM with SPL.
- Read and correlate **AWS CloudTrail** management events, S3 access logs and Azure AD sign-ins.
- Reconstruct a cloud kill chain: cloud initial access → discovery → credential theft (IMDS) → disable logging → persistence → collection → exfiltration to an external account.
- Recognise cloud-native TTPs: IMDS SSRF, `StopLogging`, `CreateAccessKey`, public bucket policies, cross-account sharing.
- Turn findings into detections (Sigma / SPL correlation searches).

## Difficulty
`advanced`

## Estimated Duration
~90 minutes

## MITRE ATT&CK (Cloud Matrix)
T1078.004 · T1526 · T1580 · T1552.005 · T1098.001 · T1562.008 · T1530 · T1537. See `mitre/navigator-layer.json`.

## Skills
Cloud Security · AWS · CloudTrail · SIEM · Splunk · SPL · Threat Hunting · Incident Response

## Requirements
- Docker + Docker Compose v2
- **≥ 4 GB RAM (6 GB recommended on Apple Silicon), ≥ 8 GB disk**
- A web browser for Splunk Web

## Compatibility — amd64 only
This lab is **amd64 (x86_64) only**, on purpose: the official **Splunk container image is not published for ARM**, so there is no native ARM build to ship.
- **Supported:** Intel/AMD (`linux/amd64`) — Splunk runs natively.
- **Best-effort (unsupported):** Apple Silicon / ARM runs it **under emulation** (Docker Desktop + Rosetta/QEMU). It works, but Splunk boots slowly and uses more RAM — give Docker Desktop ≥ 6 GB. `./doctor.sh` will warn you.

## Quick Start
```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/nimbus
./deploy.sh
```
When it finishes, open **http://localhost:8000** (user `admin`, password from `.env`) and start with `index=northwind`.

## Deployment
`./deploy.sh` checks the environment, pulls Splunk (Docker Hub) and the `forge` image (GHCR), brings both up, waits until Splunk is healthy and the dataset is ingested, and prints the Splunk URL + credentials. First boot on ARM can take several minutes (emulation).

> Maintainers who want to build the forge locally instead of pulling:
> `docker compose -f docker-compose.yml -f docker-compose.build.yml build`
> (local builds use a decoy flag; the real one is injected only in CI.)

## Validation
```bash
./verify.sh   # green when splunk is healthy and the forge has finished ingesting
```

## Lab Structure
Standard SFRS layout. The scenario generator lives in `runtime/forge/`; detection content in `rules/` (Sigma + SPL); indicators in `ioc/`, `timeline/`, `mitre/`.

## Evidence
All evidence is **inside Splunk**, in `index=northwind`, across these sourcetypes:
`aws:cloudtrail` · `aws:s3:serveraccess` · `azure:signin` · `proxy:web`.

## Investigation Flow
1. `./deploy.sh`, then confirm with `./verify.sh`. Open Splunk Web (`:8000`).
2. Baseline the data: `index=northwind | stats count by sourcetype`.
3. Find the high-risk sign-in (Azure AD) and the foreign IP driving the whole campaign.
4. Follow the chain in CloudTrail: enumeration burst → IMDS SSRF (proxy) → `StopLogging` → `CreateAccessKey` → public bucket → cross-account share.
5. Decode the base64 `NOTE` env var of the backdoor Lambda to recover the flag.
6. **Answer the questions inside KrakenSOC** to earn XP.

Starter searches:
```spl
index=northwind | stats count by sourcetype
index=northwind sourcetype=azure:signin riskLevelDuringSignIn=high
index=northwind sourcetype=aws:cloudtrail eventName IN (StopLogging, DeleteTrail)
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
- `./doctor.sh` reports Docker, architecture (with the ARM emulation note), RAM, disk and port 8000.
- Port 8000 busy? Change `SPLUNK_WEB_PORT` in `.env`.
- Splunk slow to start on ARM is expected (emulation). `./verify.sh` waits for it.

## FAQ
**Does Docker grade my answers?** No. Splunk is the investigation environment; the questions, flags and scoring live in KrakenSOC.
**Where's the solution?** Encrypted in `answers/` and unlocked from KrakenSOC (SFRS §8).
**Is the data real?** No — it's synthetic and deterministic, generated by `runtime/forge/`. No real AWS account, no real PII.

## Credits
KrakenSOC / SOCForge. Scenario: Northwind Global Systems moves to the cloud.

## License
MIT — see [`LICENSE`](./LICENSE).

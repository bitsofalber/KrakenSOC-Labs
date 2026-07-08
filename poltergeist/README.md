# Poltergeist — PowerShell Threat Hunt

![difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![duration](https://img.shields.io/badge/duration-60m-blue)
![SFRS](https://img.shields.io/badge/SFRS-1.0.0-6f42c1)
![class](https://img.shields.io/badge/class-interactive-9cf)
![platform](https://img.shields.io/badge/platform-amd64%20only-orange)
![SIEM](https://img.shields.io/badge/SIEM-Splunk-black)

> Official KrakenSOC Runtime Lab (interactive class). SOCForge owns the questions, XP and progress; this runtime owns a **real Splunk** with the PowerShell activity already indexed.

## Overview
PowerShell is one of the most abused tools on Windows. Poltergeist spins up a **real Splunk** pre-loaded with a day of PowerShell activity from Northwind's Windows fleet — benign admin scripts mixed with an attacker's encoded commands, download cradles, hidden-window execution, AV tampering, credential dumping, persistence and **log clearing**. You hunt it all with real **SPL** and recover the operator's flag by decoding an obfuscated command.

## Scenario
Northwind's EDR flagged a spike in PowerShell across the Sales fleet. Script Block Logging (Event ID 4104) and Sysmon process creation are in Splunk. The attacker even tried to wipe the Security log — but the SIEM already had it. Reconstruct what they did and find the flag.

## Architecture
Two containers on an isolated network:
- **splunk** — Splunk Enterprise (official image), HEC enabled, index `northwind`.
- **forge** — a deterministic data-forge that generates the PowerShell dataset and ingests it via HEC, then idles.

```
forge ──HEC──▶ Splunk (index=northwind)  ◀── you (Splunk Web :8000, real SPL)
```

Everything is **synthetic** and **reproducible** (fixed seed) — the answers are stable.

## Learning Objectives
- Hunt malicious PowerShell in a real SIEM with SPL.
- Detect encoded commands, download cradles, hidden windows and Office→PowerShell chains.
- Spot defense evasion (AV tampering, log clearing) and credential dumping.
- Decode obfuscation (`-EncodedCommand` base64) to recover evidence.
- Turn findings into detections (SPL / Sigma).

## Difficulty
`intermediate`

## Estimated Duration
~60 minutes

## MITRE ATT&CK
T1059.001 · T1027 · T1105 · T1562.001 · T1070.001 · T1003 · T1547.001. See `mitre/navigator-layer.json`.

## Skills
SIEM · Splunk · SPL · Threat Hunting · Detection Engineering · PowerShell Analysis

## Requirements
- Docker + Docker Compose v2
- **≥ 4 GB RAM (6 GB recommended on Apple Silicon), ≥ 8 GB disk**
- A web browser for Splunk Web

## Compatibility — amd64 only
This lab is **amd64 (x86_64) only**: the official **Splunk container image is not published for ARM**.
- **Supported:** Intel/AMD (`linux/amd64`) — Splunk runs natively.
- **Best-effort (unsupported):** Apple Silicon / ARM runs it **under emulation** (Docker Desktop + Rosetta/QEMU) — slower boot, more RAM (give Docker ≥ 6 GB). `./doctor.sh` warns you.

## Quick Start
```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/poltergeist
./deploy.sh
```
When it finishes, open **http://localhost:8000** (user `admin`, password from `.env`) and start with `index=northwind`.

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
All evidence is **inside Splunk**, in `index=northwind`:
- `sourcetype=Sysmon` — process creation (EventID 1) and network (EventID 3).
- `sourcetype=WinEventLog:Microsoft-Windows-PowerShell/Operational` — Script Block Logging (EventID 4104).

## Investigation Flow
1. `./deploy.sh`, then `./verify.sh`. Open Splunk Web (`:8000`).
2. Baseline: `index=northwind sourcetype=Sysmon EventID=1 | stats count by event_type`.
3. Hunt the techniques: encoded commands, cradles, Office→PowerShell, AV tampering, log clearing, Mimikatz.
4. Identify patient zero (the busiest malicious host) and the C2/download domains.
5. Decode the `-EncodedCommand` that hides the flag.
6. **Answer the questions inside KrakenSOC** to earn XP.

Starter searches:
```spl
index=northwind sourcetype=Sysmon EventID=1 CommandLine="*-EncodedCommand*"
index=northwind sourcetype=Sysmon EventID=1 (ParentImage="*winword.exe" OR ParentImage="*excel.exe")
index=northwind sourcetype=Sysmon EventID=1 (CommandLine="*wevtutil*" OR CommandLine="*Clear-EventLog*")
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
KrakenSOC / SOCForge. Scenario: Northwind Global Systems. Inspired by community PowerShell-detection projects; content, dataset and code are original.

## License
MIT — see [`LICENSE`](./LICENSE).

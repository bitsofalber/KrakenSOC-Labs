# Overwatch — Northwind SOC Shift

![difficulty](https://img.shields.io/badge/difficulty-advanced-red)
![duration](https://img.shields.io/badge/duration-90m-blue)
![SFRS](https://img.shields.io/badge/SFRS-1.0.0-6f42c1)
![class](https://img.shields.io/badge/class-interactive-9cf)
![SIEM](https://img.shields.io/badge/SIEM-Splunk-black)

> Official KrakenSOC Runtime Lab (interactive class). SOCForge owns the questions, XP and progress; this runtime owns a **real Splunk** with the campaign already indexed.

## Overview
Overwatch is the **SIEM capstone** of the Northwind universe. Docker spins up a **real Splunk** with a full intrusion already indexed across multiple log sources. You open Splunk Web, write real **SPL**, and correlate the whole kill chain — the same campaign you met, fragment by fragment, in *Plain Sight*, *Ghost Protocol* and *Silent Harvest*, now seen from the SOC's god-view.

## Scenario
An EDR alert and an "impossible travel" sign-in put the SOC on alert for **Northwind Global Systems**. Somewhere in a day of logs — Windows/Sysmon, Zeek, web proxy and Azure AD — a compromised account, a beaconing implant and a data exfiltration are hiding among the noise. Your shift: reconstruct what happened, end to end, and recover the operator's flag.

## Architecture
Two containers on an isolated network:
- **splunk** — Splunk Enterprise (official image) with HEC enabled and the `northwind` index.
- **forge** — a deterministic data-forge that generates the multi-source dataset and ingests it via HEC, then idles.

```
forge ──HEC──▶ Splunk (index=northwind)  ◀── you (Splunk Web :8000, real SPL)
```

Everything is **synthetic** and **reproducible** (fixed seed) — the answers are stable.

## Learning Objectives
- Investigate a real intrusion in a real SIEM with SPL.
- Correlate across sources (Sysmon, WinEventLog, Zeek, proxy, Azure AD).
- Reconstruct a kill chain: initial access → execution → C2 → collection → exfiltration.
- Decode obfuscation found in logs (PowerShell `-EncodedCommand`, base32 DNS).
- Turn findings into detections (Sigma / SPL correlation searches).

## Difficulty
`advanced`

## Estimated Duration
~90 minutes

## MITRE ATT&CK
T1078 · T1059.001 · T1071.001 · T1048.003 · T1132.001 · T1005. See `mitre/navigator-layer.json`.

## Skills
SIEM · Splunk · SPL · Threat Hunting · Incident Response · Log Correlation

## Requirements
- Docker + Docker Compose v2
- **≥ 4 GB RAM (6 GB recommended on Apple Silicon), ≥ 8 GB disk**
- A web browser for Splunk Web

## Compatibility — important note on architecture
The official **Splunk image is amd64-only**. This lab runs:
- **Natively** on Intel/AMD (`linux/amd64`).
- **Under emulation** on Apple Silicon / ARM (Docker Desktop + Rosetta/QEMU): it works, but Splunk takes a few minutes to boot and uses more RAM. Give Docker Desktop ≥ 6 GB.
`./doctor.sh` detects your architecture and warns accordingly. The `forge` image is native multi-arch.

## Quick Start
```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/overwatch
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
`Sysmon` · `WinEventLog:Security` · `zeek:dns` · `zeek:http` · `proxy:web` · `azuread:signin`.

## Investigation Flow
1. `./deploy.sh`, then confirm with `./verify.sh`. Open Splunk Web (`:8000`).
2. Baseline the data: `index=northwind | stats count by sourcetype`.
3. Find the suspicious sign-in (Azure AD), the executed implant (Sysmon), and its C2 (proxy/Zeek).
4. Quantify the beaconing (count + interval), then the DNS exfiltration.
5. Decode the PowerShell `-EncodedCommand` to recover the flag.
6. **Answer the questions inside KrakenSOC** to earn XP.

Starter searches:
```spl
index=northwind | stats count by sourcetype
index=northwind sourcetype=azuread:signin riskLevel=high
index=northwind sourcetype=Sysmon EventID=1 CommandLine="*-EncodedCommand*"
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
**Is the data real?** No — it's synthetic and deterministic, generated by `runtime/forge/`. No real PII.

## Credits
KrakenSOC / SOCForge. Scenario: Northwind Global Systems. The capstone that unifies Plain Sight, Ghost Protocol and Silent Harvest.

## License
MIT — see [`LICENSE`](./LICENSE).

# Battering Ram — Authentication Attack Hunt

![difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![duration](https://img.shields.io/badge/duration-60m-blue)
![SFRS](https://img.shields.io/badge/SFRS-1.0.0-6f42c1)
![class](https://img.shields.io/badge/class-interactive-9cf)
![platform](https://img.shields.io/badge/platform-amd64%20only-orange)
![SIEM](https://img.shields.io/badge/SIEM-Splunk-black)

> Official KrakenSOC Runtime Lab (interactive class). SOCForge owns the questions, XP and progress; this runtime owns a **real Splunk** with the authentication logs already indexed.

## Overview
Battering Ram spins up a **real Splunk** pre-loaded with a wave of authentication attacks against Northwind's Windows domain. Somewhere in a flood of failed logins, an attacker is running **password spraying** and **brute force**, locking accounts out, and eventually landing **one valid login** — then creating a backdoor admin account. You hunt it all with real **SPL**.

## Scenario
Northwind's SOC sees a spike in failed logons across the domain. Windows Security logs (4625, 4740, 4624, 4720, 4732) are in Splunk. Distinguish spraying from brute force, find the attacker's IP, the account they cracked, the accounts they locked, and the backdoor they planted — then recover the operator's flag.

## Architecture
Two containers on an isolated network:
- **splunk** — Splunk Enterprise (official image), HEC enabled, index `northwind`.
- **forge** — a deterministic data-forge that generates the auth-attack dataset and ingests it via HEC, then idles.

```
forge ──HEC──▶ Splunk (index=northwind)  ◀── you (Splunk Web :8000, real SPL)
```

Everything is **synthetic** and **reproducible** (fixed seed) — the answers are stable.

## Learning Objectives
- Hunt authentication attacks in a real SIEM with SPL.
- Distinguish password spraying (one password → many accounts) from targeted brute force (one account → many passwords).
- Pivot from failed logons to the successful compromise (4624 from the attacker IP).
- Spot post-compromise persistence: account creation (4720) and privilege escalation (4732).
- Turn findings into detections (SPL / Sigma).

## Difficulty
`intermediate`

## Estimated Duration
~60 minutes

## MITRE ATT&CK
T1110 · T1110.003 · T1078 · T1136.001 · T1098. See `mitre/navigator-layer.json`.

## Skills
SIEM · Splunk · SPL · Threat Hunting · Authentication Attacks · Windows Event Logs

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
cd KrakenSOC-Labs/battering-ram
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
- `sourcetype=WinEventLog:Security` — 4625 (failed), 4740 (lockout), 4624 (success), 4720 (account created), 4732 (added to group).
- `sourcetype=Sysmon` — post-compromise process creation.

## Investigation Flow
1. `./deploy.sh`, then `./verify.sh`. Open Splunk Web (`:8000`).
2. Baseline the failures: `index=northwind sourcetype=WinEventLog:Security EventCode=4625 | stats count by Source_Network_Address`.
3. Spraying vs brute force: count distinct accounts per source IP, and failures per account.
4. Find the successful 4624 from the attacker IP — that's the cracked account.
5. Follow persistence (4720/4732) and decode the `-EncodedCommand` for the flag.
6. **Answer the questions inside KrakenSOC** to earn XP.

Starter searches:
```spl
index=northwind sourcetype=WinEventLog:Security EventCode=4625 | stats dc(Account_Name) by Source_Network_Address
index=northwind sourcetype=WinEventLog:Security EventCode=4740
index=northwind sourcetype=WinEventLog:Security (EventCode=4720 OR EventCode=4732)
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
KrakenSOC / SOCForge. Scenario: Northwind Global Systems. Content, dataset and code are original.

## License
MIT — see [`LICENSE`](./LICENSE).

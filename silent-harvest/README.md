# Silent Harvest

![difficulty](https://img.shields.io/badge/difficulty-intermediate-orange)
![duration](https://img.shields.io/badge/duration-45m-blue)
![SFRS](https://img.shields.io/badge/SFRS-1.0.0-6f42c1)
![platforms](https://img.shields.io/badge/platforms-amd64%20%7C%20arm64-informational)
![MITRE](https://img.shields.io/badge/ATT%26CK-T1048.003%20%7C%20T1071.004-red)

> Official KrakenSOC Runtime Lab. SOCForge owns the questions, XP and progress; this runtime owns the environment and the evidence.

## Overview
A workstation at **Northwind Global Systems** is quietly leaking a payroll file off the network. There is no obvious upload, no HTTP POST, no email — only DNS. Your job is to prove **data exfiltration over DNS**, quantify it, and recover what was stolen.

## Scenario
The Sales endpoint `NW-WKS-014` was flagged by an analyst for "odd DNS volume". Egress DNS was captured. Somewhere in that noise, a sensitive HR file is being tunneled out one query at a time.

## Architecture
Three containers on an isolated network:
- **victim** — the compromised endpoint; generates benign browsing DNS **and** exfiltrates the payroll file.
- **resolver** — the attacker's C2 nameserver, answering every query (benign + exfil).
- **sniffer** — captures all DNS to `pcaps/dns-exfil.pcap` (your evidence). Shares the resolver's network namespace so it sees everything.

```
victim ──DNS──▶ resolver ◀── sniffer (tcpdump ▶ pcaps/dns-exfil.pcap)
```

## Learning Objectives
- Recognise DNS tunneling / exfiltration patterns in a packet capture.
- Distinguish high-entropy encoded subdomains from legitimate DNS noise.
- Quantify an exfiltration (queries, bytes) and reconstruct the stolen file.
- Map the activity to MITRE ATT&CK and write detection rules.

## Difficulty
`intermediate`

## Estimated Duration
~45 minutes

## MITRE ATT&CK
- **T1048.003** — Exfiltration Over Unencrypted Non-C2 Protocol (DNS)
- **T1071.004** — Application Layer Protocol: DNS
See `mitre/navigator-layer.json`.

## Skills
Network Forensics · Wireshark / tshark · DNS · Data Exfiltration Analysis

## Requirements
- Docker + Docker Compose v2 · `linux/amd64` or `linux/arm64`
- ≥ 2 GB RAM, ≥ 4 GB disk · Wireshark / tshark to analyse the capture

## Compatibility — Apple Silicon (ARM) & Intel/AMD
This lab runs **natively on both architectures** — there is **no separate ARM or AMD version**.
The images are built from multi-arch bases (`python:3.12-slim`, `alpine`), so `docker compose build`
produces images for **your** machine's architecture automatically:

| Your machine | Architecture | Status |
| :-- | :-- | :-- |
| Mac M1/M2/M3/M4, ARM PCs | `arm64` | ✅ native |
| Intel/AMD PCs, Intel Mac | `amd64` | ✅ native |

`./doctor.sh` detects your architecture and stops early with a clear message if it is unsupported.
Nothing to choose, nothing to configure — the same `./deploy.sh` works everywhere.
> Verified: images build on `arm64` (native) and `amd64` (buildx). Prebuilt GHCR images (see `.github/workflows/release.yml`) publish a single multi-arch manifest, so students always `pull` the right variant.

## Quick Start
```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/silent-harvest
./deploy.sh
```

## Deployment
`./deploy.sh` checks the environment, brings up the three containers, and waits until the capture is running and the exfiltration has completed. The evidence lands in `pcaps/dns-exfil.pcap`. No manual Docker commands required.

## Validation
```bash
./verify.sh   # green when sniffer + victim are healthy (capture done)
```

## Lab Structure
Standard SFRS layout. Scenario code lives in `runtime/` (resolver, victim, sniffer); detection content in `rules/`; indicators in `ioc/`, `timeline/`, `mitre/`.

## Evidence
- `pcaps/dns-exfil.pcap` — the DNS capture you investigate (generated on deploy).
- `ioc/iocs.csv`, `timeline/timeline.csv` — reference indicators and attack timeline.

## Artifacts
The exfiltrated object is a Northwind HR payroll file (PII: names, roles, IBANs, salaries, SSNs). Recovering it is part of the investigation.

## Investigation Flow
1. `./deploy.sh`, then confirm with `./verify.sh`.
2. Open `pcaps/dns-exfil.pcap` in Wireshark (filter `dns`).
3. Find the parent domain receiving many long, random-looking subdomains.
4. Quantify the data-carrying queries and identify the encoding.
5. Reconstruct the file and recover the flag.
6. **Answer the questions inside KrakenSOC** to earn XP.

Starter filters:
```bash
tshark -r pcaps/dns-exfil.pcap -Y 'dns.flags.response==0' -T fields -e dns.qry.name | sort | uniq -c | sort -rn | head
```

## Reset
```bash
./reset.sh    # regenerate a fresh capture from scratch
```

## Destroy
```bash
./destroy.sh  # remove containers, network, volumes and the generated pcap
```

## Troubleshooting
- `./doctor.sh` reports Docker, architecture, RAM, disk and port status.
- Empty pcap? Ensure the `sniffer` and `victim` are healthy (`./verify.sh`) and re-run `./reset.sh`.

## FAQ
**Does Docker grade my answers?** No. The runtime only produces the environment and evidence. Questions, flags, hints and scoring live in KrakenSOC.
**Where's the solution?** Encrypted in `answers/` and unlocked from KrakenSOC (SFRS §8).
**Instructor mode?** Set `INSTRUCTOR_MODE=1` in `.env` to have the C2 reconstruct the stolen file into `pcaps/` as proof.

## Credits
KrakenSOC / SOCForge. Scenario: Northwind Global Systems.

## License
MIT — see [`LICENSE`](./LICENSE).

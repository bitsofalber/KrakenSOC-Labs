# Ghost Protocol

![difficulty](https://img.shields.io/badge/difficulty-advanced-red)
![duration](https://img.shields.io/badge/duration-60m-blue)
![SFRS](https://img.shields.io/badge/SFRS-1.0.0-6f42c1)
![platforms](https://img.shields.io/badge/platforms-amd64%20%7C%20arm64-informational)
![MITRE](https://img.shields.io/badge/ATT%26CK-T1071.001%20%7C%20T1132.001%20%7C%20T1041-red)

> Official KrakenSOC Runtime Lab. SOCForge owns the questions, XP and progress; this runtime owns the environment and the evidence.

## Overview
A workstation at **Northwind Global Systems** is compromised by a malleable-C2 implant. It **beacons** to an HTTP C2 on a regular (jittered) interval, hidden among ordinary web traffic, and when tasked it exfiltrates a customer file — compressed and encoded — back over the C2 channel. Your job is to spot the beacon in the noise, fingerprint the implant, and **peel back the encoding layers** to recover what was stolen.

## Scenario
Egress HTTP from `NW-WKS-014` was captured after an EDR alert for "repetitive outbound requests". Buried among benign browsing, an implant checks in to `cdn-edge-sync.net` on a fixed cadence, carries a base64 session cookie and a distinctive User-Agent, and — on one check-in — is tasked to steal a file and upload it as `base64(gzip(...))`. Nothing is decrypted for you: the challenge is recognising the pattern and decoding the layers.

## Architecture
Three containers on an isolated network:
- **c2** — the attacker's HTTP Team Server; answers beacons, hands out one encoded task, receives the encoded results.
- **implant** — the compromised endpoint; beacons with jitter among benign noise, then exfiltrates a local customer file.
- **sniffer** — captures all HTTP to `pcaps/ghost-protocol.pcap` (your evidence). Shares the c2's network namespace so it sees everything.

```
implant ──HTTP beacon/exfil──▶ c2 ◀── sniffer (tcpdump ▶ pcaps/ghost-protocol.pcap)
```

## Learning Objectives
- Identify C2 beaconing (periodicity + jitter) hidden in benign web traffic.
- Fingerprint an implant by its endpoint, User-Agent and session cookie.
- Quantify the beaconing and locate the exfiltration request.
- Decode layered obfuscation (base64 → gzip) to recover the stolen data.
- Map the activity to MITRE ATT&CK and write detection rules.

## Difficulty
`advanced`

## Estimated Duration
~60 minutes

## MITRE ATT&CK
- **T1071.001** — Application Layer Protocol: Web Protocols
- **T1132.001** — Data Encoding: Standard Encoding
- **T1041** — Exfiltration Over C2 Channel
See `mitre/navigator-layer.json`.

## Skills
Network Forensics · Wireshark / tshark · C2 / Beacon Analysis · Malware Traffic Analysis · Data Decoding

## Requirements
- Docker + Docker Compose v2 · `linux/amd64` or `linux/arm64`
- ≥ 2 GB RAM, ≥ 4 GB disk · Wireshark / tshark; CyberChef or base64/gzip tooling to decode

## Compatibility — Apple Silicon (ARM) & Intel/AMD
This lab runs **natively on both architectures** — there is **no separate ARM or AMD version**.
The images are built from multi-arch bases (`python:3.12-slim`, `alpine`), so the same
`docker compose` works everywhere and Docker pulls the correct variant automatically:

| Your machine | Architecture | Status |
| :-- | :-- | :-- |
| Mac M1/M2/M3/M4, ARM PCs | `arm64` | native |
| Intel/AMD PCs, Intel Mac | `amd64` | native |

`./doctor.sh` detects your architecture and stops early with a clear message if it is unsupported.
> Prebuilt GHCR images (see `.github/workflows/release-ghost-protocol.yml`) publish a single multi-arch manifest, so students always `pull` the right variant.

## Quick Start
```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/ghost-protocol
./deploy.sh
```

## Deployment
`./deploy.sh` checks the environment, **pulls the prebuilt multi-arch images from GHCR**
(`ghcr.io/bitsofalber/ghost-protocol-*` — no local compilation), brings up the three containers,
and waits until the capture is running and the C2 campaign has completed. The evidence lands in
`pcaps/ghost-protocol.pcap`. No manual Docker commands required.

> Maintainers who want to build locally instead of pulling:
> `docker compose -f docker-compose.yml -f docker-compose.build.yml build`
> (local builds use a decoy dataset; the real one is injected only in CI).

## Validation
```bash
./verify.sh   # green when c2 + sniffer + implant are healthy (campaign done)
```

## Lab Structure
Standard SFRS layout. Scenario code lives in `runtime/` (c2, implant, sniffer); detection content in `rules/`; indicators in `ioc/`, `timeline/`, `mitre/`.

## Evidence
- `pcaps/ghost-protocol.pcap` — the HTTP capture you investigate (generated on deploy).
- `ioc/iocs.csv`, `timeline/timeline.csv` — reference indicators and attack timeline.

## Artifacts
The exfiltrated object is a Northwind customer file (PII: companies, contacts, emails, phones, credit lines). Recovering it — by decoding the C2 upload — is part of the investigation.

## Investigation Flow
1. `./deploy.sh`, then confirm with `./verify.sh`.
2. Open `pcaps/ghost-protocol.pcap` in Wireshark (filter `http`).
3. Spot the repeating GET to the same endpoint with a fixed cookie/User-Agent — that's the beacon. Count the check-ins.
4. Find the single `POST` to the C2 (the exfiltration) and grab its body.
5. Decode the body: base64, then gunzip → the stolen file. Recover the flag inside.
6. **Answer the questions inside KrakenSOC** to earn XP.

Starter filters:
```bash
# beacons (check-ins) and their User-Agent
tshark -r pcaps/ghost-protocol.pcap -Y 'http.request.uri=="/api/v2/status"' \
  -T fields -e http.host -e http.user_agent | sort | uniq -c
# the exfil POST body, decoded
tshark -r pcaps/ghost-protocol.pcap -Y 'http.request.method=="POST"' -T fields -e http.file_data \
  | tr -d '\n' | base64 -d | gunzip
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
- Empty pcap? Ensure the `sniffer` and `implant` are healthy (`./verify.sh`) and re-run `./reset.sh`.
- The exfil is a single POST — if you miss it, follow the C2 conversation and look for the `POST /api/v2/submit`.

## FAQ
**Does Docker grade my answers?** No. The runtime only produces the environment and evidence. Questions, flags, hints and scoring live in KrakenSOC.
**Where's the solution?** Encrypted in `answers/` and unlocked from KrakenSOC (SFRS §8).
**Instructor mode?** Set `INSTRUCTOR_MODE=1` in `.env` to have the C2 reconstruct the stolen file into `pcaps/` as proof.

## Credits
KrakenSOC / SOCForge. Scenario: Northwind Global Systems.

## License
MIT — see [`LICENSE`](./LICENSE).

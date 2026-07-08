# Plain Sight

![difficulty](https://img.shields.io/badge/difficulty-beginner-brightgreen)
![duration](https://img.shields.io/badge/duration-30m-blue)
![SFRS](https://img.shields.io/badge/SFRS-1.0.0-6f42c1)
![platforms](https://img.shields.io/badge/platforms-amd64%20%7C%20arm64-informational)
![MITRE](https://img.shields.io/badge/ATT%26CK-T1040%20%7C%20T1071.001-red)

> Official KrakenSOC Runtime Lab. SOCForge owns the questions, XP and progress; this runtime owns the environment and the evidence.

## Overview
An employee at **Northwind Global Systems** signs in to an internal portal that was never migrated to HTTPS. The login travels over plain HTTP, so the username, password and session token are all sitting **in plain sight** on the wire. Your job is to open the capture, follow the conversation and recover the credentials and the leaked API token.

## Scenario
The Sales team still uses the legacy **Sales Ops Portal** (`http://portal`, no TLS — migration ticket IT-4471 is "pending"). Egress traffic from the workstation `NW-WKS-014` was captured. Somewhere in that HTTP is a `POST /login` carrying a real account's credentials, and the response hands back an API token — none of it encrypted.

## Architecture
Three containers on an isolated network:
- **portal** — the legacy web app; serves benign pages **and** the cleartext `/login` that returns the API token.
- **workstation** — the employee endpoint; browses a little, then logs in over HTTP.
- **sniffer** — captures all HTTP to `pcaps/cleartext-http.pcap` (your evidence). Shares the portal's network namespace so it sees everything.

```
workstation ──HTTP──▶ portal ◀── sniffer (tcpdump ▶ pcaps/cleartext-http.pcap)
```

## Learning Objectives
- Open a PCAP and isolate HTTP traffic in Wireshark / tshark.
- Follow an HTTP stream and read a `POST /login` request body.
- Extract cleartext credentials and a leaked session/API token from the wire.
- Understand why unencrypted application protocols enable credential sniffing.
- Map the activity to MITRE ATT&CK and write detection rules.

## Difficulty
`beginner`

## Estimated Duration
~30 minutes

## MITRE ATT&CK
- **T1040** — Network Sniffing
- **T1071.001** — Application Layer Protocol: Web Protocols
- **T1078** — Valid Accounts
See `mitre/navigator-layer.json`.

## Skills
Network Forensics · Wireshark / tshark · HTTP · Credential Analysis

## Requirements
- Docker + Docker Compose v2 · `linux/amd64` or `linux/arm64`
- ≥ 2 GB RAM, ≥ 4 GB disk · Wireshark / tshark to analyse the capture

## Compatibility — Apple Silicon (ARM) & Intel/AMD
This lab runs **natively on both architectures** — there is **no separate ARM or AMD version**.
The images are built from multi-arch bases (`python:3.12-slim`, `alpine`), so the same
`docker compose` works everywhere and Docker pulls the correct variant automatically:

| Your machine | Architecture | Status |
| :-- | :-- | :-- |
| Mac M1/M2/M3/M4, ARM PCs | `arm64` | native |
| Intel/AMD PCs, Intel Mac | `amd64` | native |

`./doctor.sh` detects your architecture and stops early with a clear message if it is unsupported.
Nothing to choose, nothing to configure — the same `./deploy.sh` works everywhere.
> Prebuilt GHCR images (see `.github/workflows/release-plain-sight.yml`) publish a single multi-arch manifest, so students always `pull` the right variant.

## Quick Start
```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/plain-sight
./deploy.sh
```

## Deployment
`./deploy.sh` checks the environment, **pulls the prebuilt multi-arch images from GHCR**
(`ghcr.io/bitsofalber/plain-sight-*` — no local compilation), brings up the three containers,
and waits until the capture is running and the login has completed. The evidence lands in
`pcaps/cleartext-http.pcap`. No manual Docker commands required.

> Maintainers who want to build locally instead of pulling:
> `docker compose -f docker-compose.yml -f docker-compose.build.yml build`
> (local builds use a decoy token; the real token is injected only in CI).

## Validation
```bash
./verify.sh   # green when portal + sniffer + workstation are healthy (capture done)
```

## Lab Structure
Standard SFRS layout. Scenario code lives in `runtime/` (portal, workstation, sniffer); detection content in `rules/`; indicators in `ioc/`, `timeline/`, `mitre/`.

## Evidence
- `pcaps/cleartext-http.pcap` — the HTTP capture you investigate (generated on deploy).
- `ioc/iocs.csv`, `timeline/timeline.csv` — reference indicators and attack timeline.

## Artifacts
The exposed objects are a Northwind sales account's credentials and the API token the portal returns after login. Recovering them from the capture is the whole exercise.

## Investigation Flow
1. `./deploy.sh`, then confirm with `./verify.sh`.
2. Open `pcaps/cleartext-http.pcap` in Wireshark (filter `http`).
3. Find the `POST /login` request and **Follow HTTP Stream**.
4. Read the username and password from the request body.
5. Read the API token the server returns (header / cookie / body) — that's the flag.
6. **Answer the questions inside KrakenSOC** to earn XP.

Starter filters:
```bash
tshark -r pcaps/cleartext-http.pcap -Y 'http.request.method == "POST"' \
  -T fields -e http.request.uri -e http.file_data
tshark -r pcaps/cleartext-http.pcap -Y 'http.response' \
  -T fields -e http.response.code -e http.response.line
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
- Empty pcap? Ensure the `sniffer` and `workstation` are healthy (`./verify.sh`) and re-run `./reset.sh`.

## FAQ
**Does Docker grade my answers?** No. The runtime only produces the environment and evidence. Questions, flags, hints and scoring live in KrakenSOC.
**Where's the solution?** Encrypted in `answers/` and unlocked from KrakenSOC (SFRS §8).
**Is the portal doing anything malicious?** No — the vulnerability is the protocol. Cleartext HTTP exposes everything the workstation sends and receives.

## Credits
KrakenSOC / SOCForge. Scenario: Northwind Global Systems.

## License
MIT — see [`LICENSE`](./LICENSE).

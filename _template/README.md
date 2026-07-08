<!-- SFRS README standard (§6). Copy this file when creating a new lab. -->
# Runtime Lab Template

![difficulty](https://img.shields.io/badge/difficulty-beginner-brightgreen)
![duration](https://img.shields.io/badge/duration-30m-blue)
![SFRS](https://img.shields.io/badge/SFRS-1.0.0-6f42c1)
![platforms](https://img.shields.io/badge/platforms-amd64%20%7C%20arm64-informational)

> **This is the golden reference lab.** Copy `_template/` to start a new SFRS-compliant Runtime Lab,
> then replace the placeholder environment with your real scenario.
> Official runtime extension of **KrakenSOC** — SOCForge owns the questions, XP and progress; this repo owns the environment.

## Overview
A minimal, working KrakenSOC Runtime Lab: a target web service plus a telemetry sensor. It exists to demonstrate the standard structure, scripts and manifest that every lab must follow.

## Scenario
_Replace with the incident narrative (set at **Northwind Global Systems**)._

## Architecture
Two containers on an isolated network: `web` (target) and `sensor` (emits telemetry to `telemetry/`). See `docs/` for the diagram.

## Learning Objectives
- Understand the SFRS lab lifecycle (`deploy → verify → investigate → reset → destroy`).
- _Add scenario-specific objectives._

## Difficulty
`beginner`

## Estimated Duration
~30 minutes

## MITRE ATT&CK
See `manifest.yaml` (`mitre:`) and `mitre/` (ATT&CK Navigator layer).

## Skills
Docker · Log Analysis _(extend per scenario)._

## Requirements
- Docker + Docker Compose v2
- `linux/amd64` or `linux/arm64`
- ≥ 2 GB RAM, ≥ 4 GB disk free

## Compatibility — Apple Silicon (ARM) & Intel/AMD
Every SFRS lab runs **natively on both architectures** — never ship a separate ARM/AMD version.
Use multi-arch base images (or publish multi-arch images to GHCR via `.github/workflows/release.yml`).
`docker compose build` targets the host architecture automatically and `./doctor.sh` validates it.
The same `./deploy.sh` works on Mac Apple Silicon and Intel/AMD alike.

## Quick Start
```bash
git clone https://github.com/<org-or-user>/<lab-id>.git
cd <lab-id>
./deploy.sh
```

## Deployment
`./deploy.sh` runs `doctor.sh`, creates `.env`, pulls multi-arch images, starts the environment and waits until every container is healthy. No manual Docker commands required.

## Validation
```bash
./verify.sh   # exits 0 only when every container is running & healthy
```

## Lab Structure
Standard SFRS layout — see [`SOCFORGE-RUNTIME-SPEC.md`](../SOCFORGE-RUNTIME-SPEC.md) §3.

## Evidence
Generated telemetry lands in `telemetry/`; shipped evidence lives in `artifacts/`, `pcaps/`, `ioc/`, `timeline/`.

## Artifacts
_List the concrete evidence files the student will analyse._

## Investigation Flow
1. `./deploy.sh` and confirm health with `./verify.sh`.
2. Collect evidence from `telemetry/` / `artifacts/`.
3. Answer the questions **inside KrakenSOC** to earn XP.

## Reset
```bash
./reset.sh    # back to pristine state, no full re-download
```

## Destroy
```bash
./destroy.sh  # remove containers, network, volumes and generated temp files
```

## Troubleshooting
Run `./doctor.sh` — it reports Docker status, architecture, RAM, disk and port conflicts with actionable messages.

## FAQ
**Does Docker grade my answers?** No. The runtime only provides the environment. Questions, flags, hints and scoring live in KrakenSOC.

## Credits
KrakenSOC / SOCForge.

## License
See [`LICENSE`](./LICENSE).

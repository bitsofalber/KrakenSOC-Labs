# SOCForge Runtime Specification (SFRS)

**Version:** 1.0.0
**Status:** Stable
**Applies to:** every KrakenSOC Docker Runtime Lab

> A Runtime Lab is **not** a standalone project. It is an **official runtime extension of KrakenSOC**.
> SOCForge (the SaaS) owns learning, questions, scoring and progress.
> The runtime owns only the **local execution environment**: containers, logs, artifacts, PCAPs, telemetry, evidence.
>
> This specification defines the contract every lab MUST comply with so that dozens or hundreds of labs
> can be maintained — and eventually community-authored — with one consistent student and developer experience.

---

## 1. Principles

1. **Separation of concerns.** The runtime never evaluates answers, never stores XP, never owns progress. It only produces a realistic environment and the evidence to investigate it. Questions, flags, hints, scoring, achievements and career all live in KrakenSOC.
2. **One command to run.** A student runs `./deploy.sh` (or `forge install <lab>`). No manual `docker` commands are ever required.
3. **Deterministic & resettable.** `reset.sh` returns the lab to its pristine state; `destroy.sh` removes every trace. Two runs of the same version produce the same evidence.
4. **Standardized.** Identical folder layout, identical script names and behaviour, identical manifest schema, identical README sections — for every lab, no exceptions.
5. **Machine-readable.** `manifest.yaml` is the canonical source of truth. The SaaS reads it to render the lab page. Humans never hand-copy metadata into KrakenSOC.
6. **Multi-arch by default.** Every lab runs on `linux/amd64` **and** `linux/arm64` (Intel/AMD and Apple Silicon / ARM). See §7.
7. **Solutions are protected.** Answer keys are never published in cleartext. They are encrypted and unlocked from KrakenSOC. See §8.
8. **Forward-compatible.** The layout is already compatible with the future `forge` CLI. See §9.

---

## 2. Naming conventions

| Item | Rule | Example |
| :-- | :-- | :-- |
| Repository | `kebab-case`, no `lab-`/`runtime-` prefix | `operation-black-quill` |
| Lab `id` (manifest) | equals the repo name | `operation-black-quill` |
| Docker images | `ghcr.io/<org>/<repo>/<service>` | `ghcr.io/krakensoc-labs/operation-black-quill/victim` |
| Compose project | equals the lab `id` | `-p operation-black-quill` |
| Docker network | `<id>-net` | `operation-black-quill-net` |
| Git tags / releases | SemVer, `v`-prefixed | `v1.2.0` |

One lab = one repository = independent versioning, releases, issues and documentation.

---

## 3. Repository structure (mandatory)

```
<lab-id>/
├── README.md              # follows the README standard (§6)
├── LICENSE
├── CHANGELOG.md           # Keep a Changelog + SemVer
├── manifest.yaml          # the Runtime spec for this lab (§4)
├── docker-compose.yml     # the environment (multi-arch images)
├── .env.example           # every tunable; copied to .env by deploy.sh
├── deploy.sh              # §5
├── destroy.sh             # §5
├── reset.sh               # §5
├── doctor.sh              # §5
├── verify.sh              # §5
├── runtime/               # Dockerfiles / source for custom images
├── docs/                  # extended documentation, architecture diagram
├── config/                # service configs (nginx, sysmon, zeek, suricata…)
├── seed/                  # data used to build the scenario at deploy time
├── telemetry/             # generated live telemetry (gitignored)
├── logs/                  # generated logs (gitignored)
├── pcaps/                 # generated / shipped packet captures
├── artifacts/             # evidence: office docs, scripts, registry, emails…
├── ioc/                   # indicators of compromise (csv/json/stix)
├── timeline/              # attack timeline (csv/json)
├── mitre/                 # ATT&CK mapping (navigator layer json)
├── rules/                 # detection content
│   ├── sigma/  ├── yara/  ├── suricata/  ├── snort/
│   ├── splunk/ ├── kql/   └── elastic/
├── questions/             # question DEFINITIONS only — never the answers (§8)
├── answers/               # ENCRYPTED solution bundle only (§8)
├── hints/                 # progressive hints (may be encrypted)
├── screenshots/           # for the KrakenSOC lab page
├── resources/             # links: Knowledge, Academy, external refs
└── .github/workflows/     # multi-arch build & release CI (§7)
```

Directories that hold **generated** content (`telemetry/`, `logs/`, plus `pcaps/` when produced at runtime) MUST ship a `.gitkeep` and be listed in `.gitignore`. Directories that hold **shipped** evidence keep their files in git.

---

## 4. Manifest (`manifest.yaml`)

The manifest is the official Runtime specification for a lab and the **only** thing KrakenSOC needs to render its page. It MUST validate against [`schema/manifest.schema.json`](./schema/manifest.schema.json).

Top-level keys (see `_template/manifest.yaml` for a complete, valid example):

```
spec_version            # SFRS version this lab targets, e.g. "1.0.0"
id                      # == repo name
title
version                 # SemVer of the lab
difficulty              # beginner | intermediate | advanced | expert
estimated_duration      # minutes (int)
author
license
skills[]                # e.g. ["Wireshark", "DNS", "Network Forensics"]
categories[]            # e.g. ["Network Forensics"]
tags[]
mitre:                  # tactics/techniques
  tactics[]             # e.g. ["Exfiltration"]
  techniques[]          # e.g. ["T1048.003", "T1071.004"]
attack_chain[]          # ordered human-readable steps
runtime:
  containers[]          # name, image, role, healthcheck
  ports[]               # host:container mappings exposed to the student
  supported_platforms[] # ["linux/amd64", "linux/arm64"]
  docker_images[]       # fully-qualified image refs (GHCR)
  minimum_requirements: # ram_mb, disk_mb, cpus
ioc[]                   # summary indicators (full list in ioc/)
telemetry[]             # what telemetry the lab produces (sysmon, zeek…)
evidence[]              # categories present (windows_logs, pcaps, emails…)
questions[]             # references (ids/titles) — answers stay in SaaS
flags: { count }        # how many flags, NOT the values
resources:              # links back into KrakenSOC + external
  knowledge_guides[]
  academy_modules[]
  operations[]
  investigations[]
  career_paths[]
  certifications[]
  external[]
required_tools[]        # tools the student needs (Wireshark, tshark…)
```

**Rule:** the manifest never contains answers, flag values, or decryption keys.

---

## 5. Standard scripts (contract)

Every lab ships these five scripts. They are POSIX-friendly `bash`, executable, idempotent, and driven by `docker-compose.yml` + `.env`. Exit code `0` = success, non-zero = failure.

| Script | MUST do | Behaviour |
| :-- | :-- | :-- |
| `doctor.sh` | Pre-flight checks | Docker installed & running, Docker Compose v2, host **arch** (amd64/arm64), RAM, disk, required ports free, OS, permissions, network. Friendly, actionable errors. Never mutates anything. |
| `deploy.sh` | Bring the lab up | Run `doctor.sh`; copy `.env.example`→`.env` if missing; `docker compose pull`; `docker compose up -d --build`; wait for health; print access URLs + next steps ("return to KrakenSOC to answer"). |
| `verify.sh` | Readiness gate | Confirm **every** container is running and healthy before the student starts. Non-zero if any is unhealthy. |
| `reset.sh` | Pristine state | Restore the lab to its original state (recreate volumes/seed) without a full re-download. |
| `destroy.sh` | Full teardown | Stop containers, remove the network, remove volumes, delete generated temp files (`logs/`, `telemetry/`, generated `pcaps/`). |

Scripts MUST use the lab `id` as the compose project name (`-p <id>`) so labs never collide with each other or with unrelated Docker projects on the student's machine.

---

## 6. README standard

Every README contains these sections, in this order:

`Overview` · `Scenario` · `Architecture` · `Learning Objectives` · `Difficulty` · `Estimated Duration` · `MITRE ATT&CK` · `Skills` · `Requirements` · `Quick Start` · `Deployment` · `Validation` · `Lab Structure` · `Evidence` · `Artifacts` · `Investigation Flow` · `Reset` · `Destroy` · `Troubleshooting` · `FAQ` · `Credits` · `License`

A header badge block SHOULD show: difficulty, duration, SFRS version, supported platforms, latest release.

---

## 7. Multi-architecture (AMD + ARM)

Every lab MUST run on `linux/amd64` and `linux/arm64`.

- **Prefer multi-arch base images** (official images already publish both). When only base images are used, the same `docker-compose.yml` works everywhere and Docker pulls the correct variant automatically.
- **Custom images MUST be published multi-arch.** The template ships `.github/workflows/release.yml`, which on a version tag builds with `docker buildx build --platform linux/amd64,linux/arm64` and pushes a multi-arch manifest to **GHCR**. Students always `pull` — never build — the correct architecture.
- `doctor.sh` detects the host architecture (`uname -m`) and fails early with a clear message if it is neither amd64 nor arm64.
- `manifest.runtime.supported_platforms` MUST list both platforms.

There are **no** separate "AMD compose" and "ARM compose" files. One compose, multi-arch images.

---

## 8. Solutions, questions & hints

- **Questions live in KrakenSOC.** The repo's `questions/` holds only question *definitions/ids* for reference — never the correct answers or flag values.
- **Answers are encrypted.** `answers/solution.bundle.age` (or `.gpg`) is the only answer artifact in the repo. It is encrypted; the key is held by KrakenSOC and released only when the student completes the lab or explicitly reveals it. Cleartext solutions MUST NOT be committed.
- **Hints** may be shipped progressively and encrypted the same way.

Recommended: [`age`](https://github.com/FiloSottile/age) for the encrypted bundle (`age -r <krakensoc-pubkey>`).

---

## 9. Forge CLI compatibility (future)

Labs MUST already be compatible with the planned `forge` CLI:

```
forge install <lab-id>     # resolve repo from registry, git clone, run deploy.sh
forge verify  <lab-id>     # run the lab's verify.sh
forge doctor  <lab-id>     # run the lab's doctor.sh
forge reset   <lab-id>     # run the lab's reset.sh
forge destroy <lab-id>     # run the lab's destroy.sh
forge update  <lab-id>     # git pull + re-deploy to latest release
```

`forge` only orchestrates the standard scripts and reads `manifest.yaml` + the hub `registry.yaml`. Because every lab honours the same contract, the CLI needs no per-lab code. A reference stub lives in [`cli/forge`](./cli/forge).

---

## 10. Compliance

A lab is **SFRS-compliant** when:

- [ ] Structure matches §3.
- [ ] `manifest.yaml` validates against the schema (§4) and lists both platforms.
- [ ] The five scripts exist, are executable, and honour §5.
- [ ] README has every §6 section.
- [ ] Custom images are published multi-arch to GHCR (§7).
- [ ] No cleartext answers/flags/keys anywhere in the repo (§8).
- [ ] The lab appears in the hub `registry.yaml`.

Copy `_template/` to start a new compliant lab. Third parties can author labs the same way; if it passes compliance, it can be listed in KrakenSOC.

---

## 11. Interactive labs (SIEM / tool UIs)

Most labs produce **offline evidence** (a PCAP, logs) the student analyses with their own tools. An **interactive lab** instead ships a real analysis platform (a SIEM such as Splunk or Elastic, a Zeek/Arkime UI, etc.) that the student **drives live in the browser**. Overwatch is the reference implementation.

Interactive labs follow the same contract with these additions:

- **UI over a host port.** `manifest.runtime.ports` MUST expose the tool's web port (e.g. `"8000:8000"`), and `.env.example` MUST make it overridable (`SPLUNK_WEB_PORT`) with `REQUIRED_PORTS` set so `doctor.sh` checks it is free.
- **Evidence lives inside the tool.** Use `evidence: ["siem"]` and document the index/dataset and starter queries in the README. There is no `pcaps/` deliverable.
- **A generator, not shipped evidence.** A one-shot `forge`/ingest service creates the dataset **deterministically** (fixed seed) and loads it at deploy time (e.g. Splunk HEC). Answers stay stable across runs. `reset.sh` recreates a pristine dataset (`down -v` + up re-ingests).
- **Readiness = platform healthy AND data loaded.** `verify.sh` passes only when the tool is healthy and the generator has finished (health-gated marker).
- **Credentials.** `deploy.sh` prints the URL and login. Never commit real secrets; the flag stays baked-in-CI / decoy-in-repo (§8).
- **Heavier footprint & upstream images.** SIEM images are large and may be **single-arch** (the official Splunk image is amd64-only). Such a lab is **exempt from the §7 both-platforms rule**: it declares only its supported platform in `manifest.runtime.supported_platforms` (a single entry is allowed for interactive labs), pins `platform: linux/amd64` in compose, and `doctor.sh` treats the other architecture as best-effort/unsupported (a clear WARN about emulation, not an OK). Raise `minimum_requirements` accordingly.

Everything else (naming §2, structure §3, manifest §4, the five scripts §5, README §6, protected answers §8, registry §10) applies unchanged.

---

_SOCForge // KrakenSOC — SOCForge is the brain. Docker is the execution environment. GitHub is the distribution platform._

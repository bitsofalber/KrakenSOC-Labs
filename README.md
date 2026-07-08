# KrakenSOC Runtime Labs

> The official **runtime ecosystem** of KrakenSOC. This repository is the **hub**: it holds the
> Runtime Specification, the reference template, the manifest schema, the `forge` CLI and the lab registry.

**SOCForge is the brain. Docker is the execution environment. GitHub is the distribution platform.**

>  **¿Nuevo con Docker?** Empieza por la **[Guía: Antes de empezar](./GETTING-STARTED.md)** — instalar Docker y Compose v2 en Kali, arreglar el error de `docker compose` y lanzar tu primer lab paso a paso.

Docker Runtime Labs are **not** standalone labs — they are official downloadable extensions of KrakenSOC.
Students discover a lab inside KrakenSOC, download the runtime, run one script, investigate locally, then
return to KrakenSOC to answer questions and earn XP. **Progress always belongs to KrakenSOC**, never to the runtime.

```
Discover in KrakenSOC → Download runtime (GitHub) → ./deploy.sh → Investigate locally
        ↑                                                                    │
        └──────────────  Answer questions · earn XP · unlock  ←─────────────┘
```

## What's in this hub

| Path | Purpose |
| :-- | :-- |
| [`SOCFORGE-RUNTIME-SPEC.md`](./SOCFORGE-RUNTIME-SPEC.md) | **The specification.** Every lab MUST comply. Folder structure, manifest, scripts, README, multi-arch, solutions. |
| [`_template/`](./_template) | The **golden reference lab**. Copy it to start a new SFRS-compliant lab. Working scripts + manifest + multi-arch CI. |
| [`schema/manifest.schema.json`](./schema/manifest.schema.json) | JSON Schema for `manifest.yaml` — lets KrakenSOC auto-read & validate labs. |
| [`registry.yaml`](./registry.yaml) | Machine-readable index of all labs, consumed by the SaaS and `forge`. |
| [`cli/forge`](./cli/forge) | Reference `forge` CLI (`install`, `update`, `verify`, `doctor`, `reset`, `destroy`). |

## The ecosystem in one page

- **One lab = one repository.** Independent versioning, releases, issues and docs.
- **Standardized.** Identical structure, script names/behaviour, manifest and README across every lab (SFRS).
- **Multi-arch.** Every lab runs on `linux/amd64` and `linux/arm64` via multi-arch images (not two composes).
- **Separation of concerns.** The runtime produces the environment + evidence; KrakenSOC owns questions, flags, hints, XP, achievements and career.
- **Protected solutions.** Answer keys ship encrypted and are unlocked from KrakenSOC only.
- **Future-proof.** Structure is already compatible with the `forge` CLI so labs need no per-lab tooling.

## Create a new lab

```bash
cp -r _template <lab-id>
# 1) edit <lab-id>/manifest.yaml  (validate against schema/manifest.schema.json)
# 2) replace <lab-id>/docker-compose.yml with the real scenario (multi-arch images)
# 3) fill README sections, evidence, rules, mitre, questions (defs only)
# 4) add the lab to registry.yaml
# 5) verify locally:
cd <lab-id> && ./deploy.sh && ./verify.sh && ./destroy.sh
```

A lab is publishable when it passes the **Compliance checklist** in the spec (§10).

## Run a lab (student)

```bash
git clone https://github.com/<org-or-user>/<lab-id>.git
cd <lab-id>
./deploy.sh          # doctor → pull → up → health check → URLs
# ... investigate, then answer inside KrakenSOC ...
./destroy.sh
```

Or, with the future CLI: `forge install <lab-id>`.

## Catalogue

See [`registry.yaml`](./registry.yaml). Planned labs:

`operation-black-quill` · `operation-iron-gate` · `phantom-storm` · `apt29-midnight-blizzard` ·
`silent-harvest` · `unauthorized-horizon` · `operation-root-shadow` · `operation-lockbit` · `operation-kerberos`

> The provisional per-lab folders in this repo are placeholders. Each lab migrates to its **own repository**
> (see the spec, §2) once the topology is finalized; `registry.yaml` tracks where each lives.

---

_SOCForge // KrakenSOC — Simula la amenaza. Domina la respuesta._

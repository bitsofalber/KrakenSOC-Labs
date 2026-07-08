# Changelog — Silent Harvest

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

## [1.1.0] - 2026-07-08
### Changed
- Distribución por GHCR: los alumnos hacen `pull` de imágenes multi-arch
  (amd64+arm64) ya construidas, en vez de compilar en local.
### Security
- El payload real (con la flag) sale del repositorio: se inyecta solo en el
  build de CI desde un secret. El repo contiene únicamente un decoy.

## [1.0.0] - 2026-07-08
### Added
- DNS exfiltration runtime (resolver C2 + victim + sniffer), multi-arch.
- Live-generated evidence PCAP; Sigma + Suricata detection rules; IoCs, timeline, ATT&CK layer.
- SFRS-compliant scripts, manifest and README. Encrypted solution bundle.

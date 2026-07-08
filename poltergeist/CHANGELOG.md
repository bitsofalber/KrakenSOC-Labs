# Changelog — Poltergeist

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-07-08
### Added
- Interactive-class Splunk lab (SFRS §11): a real Splunk pre-indexed with a PowerShell-attack dataset, hunted with live SPL.
- Deterministic data-forge (Sysmon EventID 1/3 + PowerShell Script Block Logging 4104) covering encoded commands, download cradles, hidden window, AV tampering, credential dumping, persistence and log clearing; IOCs reconcile with the Northwind universe.
- SPL detections + Sigma rule; IoCs, timeline, ATT&CK layer. Encrypted solution bundle.
- SFRS-compliant scripts; forge published to GHCR (Splunk pulled from Docker Hub, amd64-only).
### Security
- The real flag is kept out of the repository: injected only in the CI build from the `POLTERGEIST_TOKEN` secret. The repo ships only a decoy.

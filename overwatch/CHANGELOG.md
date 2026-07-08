# Changelog — Overwatch

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-07-08
### Added
- First **interactive-class** KrakenSOC Runtime Lab (SFRS §11): a real Splunk with the dataset pre-indexed, investigated with live SPL.
- Deterministic multi-source data-forge (Sysmon, WinEventLog, Zeek, proxy, Azure AD) telling a full Northwind intrusion; IOCs reconcile with Plain Sight, Ghost Protocol and Silent Harvest.
- Splunk detection SPL + Sigma rule; IoCs, timeline, ATT&CK layer. Encrypted solution bundle.
- SFRS-compliant scripts; forge published multi-arch to GHCR (Splunk pulled from Docker Hub, amd64 — emulated on ARM).
### Security
- The real flag is kept out of the repository: injected only in the CI build from the `OVERWATCH_TOKEN` secret. The repo ships only a decoy.

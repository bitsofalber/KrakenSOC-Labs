# Changelog — Nimbus

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-07-09
### Added
- **Cloud interactive-class** KrakenSOC Runtime Lab (SFRS §11): a real Splunk with a full AWS cloud intrusion pre-indexed, investigated with live SPL.
- Deterministic multi-source data-forge (AWS CloudTrail, S3 server access logs, Azure AD sign-ins, web proxy) telling Northwind's cloud-migration breach.
- Maps the **Cloud Matrix** of MITRE ATT&CK end to end: T1078.004, T1526, T1580, T1552.005, T1098.001, T1562.008, T1530, T1537.
- Cloud Sigma rules + investigation SPL; IoCs, timeline, ATT&CK layer. Encrypted solution bundle.
- SFRS-compliant scripts; forge published multi-arch to GHCR (Splunk pulled from Docker Hub, amd64 — emulated on ARM).
### Security
- The real flag is kept out of the repository: injected only in the CI build from the `NIMBUS_TOKEN` secret. The repo ships only a decoy.

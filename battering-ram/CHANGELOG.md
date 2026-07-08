# Changelog — Battering Ram

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-07-08
### Added
- Interactive-class Splunk lab (SFRS §11): a real Splunk pre-indexed with an authentication-attack dataset (WinEventLog:Security 4625/4740/4624/4720/4732 + Sysmon), hunted with live SPL.
- Deterministic data-forge: password spraying + targeted brute force → account lockouts → one valid compromise → backdoor account + privilege escalation.
- SPL detections + Sigma rule; IoCs, timeline, ATT&CK layer. Encrypted solution bundle.
- SFRS-compliant scripts; forge published to GHCR (Splunk pulled from Docker Hub, amd64-only).
### Security
- The real flag is kept out of the repository: injected only in the CI build from the `BATTERING_RAM_TOKEN` secret. The repo ships only a decoy.

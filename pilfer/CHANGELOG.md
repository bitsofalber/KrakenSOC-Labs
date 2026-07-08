# Changelog — Pilfer

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-07-08
### Added
- Interactive-class Splunk lab (SFRS §11): a real Splunk pre-indexed with insider-threat telemetry (WinEventLog:Security 6416/4663 + Sysmon 1/11), investigated with live SPL.
- Deterministic data-forge: USB device connection, sensitive file access, data staging (Compress-Archive) and file copy to a removable drive.
- SPL detections + Sigma rule; IoCs, timeline, ATT&CK layer. Encrypted solution bundle.
- SFRS-compliant scripts; forge published to GHCR (Splunk pulled from Docker Hub, amd64-only).
### Security
- The real flag is kept out of the repository: injected only in the CI build from the `PILFER_TOKEN` secret. The repo ships only a decoy.

# Changelog — Baited

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-07-08
### Added
- Interactive-class Splunk lab (SFRS §11): a real Splunk pre-indexed with an email-gateway phishing dataset, investigated with live SPL.
- Deterministic data-forge: typosquat senders, SPF/DKIM/DMARC results, malicious URLs and attachments, and one delivered phish that compromises s.buchanan (canon initial access). Flag hidden as a base64 token in the malicious URL.
- SPL detections (incl. phishing score) + Sigma rule; IoCs, timeline, ATT&CK layer. Encrypted solution bundle.
- SFRS-compliant scripts; forge published to GHCR (Splunk pulled from Docker Hub, amd64-only).
### Security
- The real flag is kept out of the repository: injected only in the CI build from the `BAITED_TOKEN` secret. The repo ships only a decoy.

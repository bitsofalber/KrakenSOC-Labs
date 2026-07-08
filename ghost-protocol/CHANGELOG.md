# Changelog — Ghost Protocol

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-07-08
### Added
- HTTP C2 beacon & tasking runtime (c2 Team Server + implant + sniffer), multi-arch.
- Live-generated evidence PCAP (`pcaps/ghost-protocol.pcap`): 12 jittered beacons among benign noise, one encoded task, and a base64+gzip exfil POST.
- Sigma + Suricata detection rules; IoCs, timeline, ATT&CK layer.
- SFRS-compliant scripts, manifest and README. Encrypted solution bundle.
### Security
- The real customer dataset (with the flag) is kept out of the repository: it is injected only in the CI build from the `GHOST_PROTOCOL_TOKEN` secret. The repo ships only a decoy.

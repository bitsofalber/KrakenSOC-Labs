# Changelog — Plain Sight

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-07-08
### Added
- Cleartext HTTP credential-capture runtime (legacy portal + employee workstation + sniffer), multi-arch.
- Live-generated evidence PCAP (`pcaps/cleartext-http.pcap`); Sigma + Suricata detection rules; IoCs, timeline, ATT&CK layer.
- SFRS-compliant scripts, manifest and README. Encrypted solution bundle.
### Security
- The real API token (the flag) is kept out of the repository: it is injected only in the CI build from the `PLAIN_SIGHT_TOKEN` secret. The repo ships only a decoy token.

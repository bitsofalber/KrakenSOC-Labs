# Answers (protected)

Per the SOCForge Runtime Specification (§8), the official solution is **never** published in cleartext.

- `solution.md.enc` — the answer key + reconstruction walkthrough + flag, encrypted with AES-256-CBC (PBKDF2).
- The passphrase is held by **KrakenSOC** and released only when the student completes the lab or explicitly chooses to reveal it.

To unlock (once KrakenSOC gives you the passphrase):

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in solution.md.enc -pass pass:'<passphrase>'
```

Do not commit the passphrase or any decrypted output to the repository.

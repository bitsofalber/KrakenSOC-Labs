# ftp-server — Dead Drop

Servidor FTP legacy en claro (pyftpdlib). Sirve `customers_q4_export.csv` con la
flag embebida en el pie (`export_token:`).

## Token (flag)
La flag se lee de `seed/export_token.txt`. En el repositorio ese fichero es un
**DECOY**. El token real se inyecta SOLO en el build de CI desde el secret
`DEAD_DROP_TOKEN` (ver `.github/workflows/release-dead-drop.yml`), así nunca
vive en claro en el repositorio.

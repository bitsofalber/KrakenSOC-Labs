# runtime/forge — nota de mantenedor

`seed/flag.txt` en el repo es un **DECOY** (flag falsa). El data-forge la
incrusta en el dataset generado (en la variable de entorno `NOTE`, base64, de la
Lambda de persistencia `nw-metrics-sync`). La flag REAL vive en el secret de
GitHub Actions `NIMBUS_TOKEN` y se inyecta en la imagen del forge SOLO durante el
build de CI (`.github/workflows/release-nimbus.yml`). Así la flag nunca está en
el repositorio en claro. Los alumnos hacen `pull` de la imagen de GHCR (con la
flag real); los builds locales usan el decoy.

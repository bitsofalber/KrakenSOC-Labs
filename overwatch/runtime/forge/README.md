# runtime/forge — nota de mantenedor

`seed/flag.txt` en el repo es un **DECOY** (flag falsa). El data-forge la
incrusta en el dataset generado (dentro de un PowerShell -EncodedCommand). La
flag REAL vive en el secret de GitHub Actions `OVERWATCH_TOKEN` y se inyecta en
la imagen del forge SOLO durante el build de CI
(`.github/workflows/release-overwatch.yml`). Así la flag nunca está en el
repositorio en claro. Los alumnos hacen `pull` de la imagen de GHCR (con la
flag real); los builds locales usan el decoy.

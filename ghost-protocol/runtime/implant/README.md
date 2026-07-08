# runtime/implant — nota de mantenedor

`seed/northwind_customers.csv` en el repo es un **DECOY** (flag falsa). Es el
fichero LOCAL de la víctima que el implante exfiltra. El dataset REAL (con la
flag verdadera) vive en el secret de GitHub Actions `GHOST_PROTOCOL_TOKEN` y se
inyecta en la imagen del implante SOLO durante el build de CI
(`.github/workflows/release-ghost-protocol.yml`). Así la flag nunca está en el
repositorio en claro. Los alumnos hacen `pull` de la imagen de GHCR (con el
dataset real); los builds locales usan el decoy.

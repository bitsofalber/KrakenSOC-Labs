# runtime/victim — nota de mantenedor

`seed/northwind_payroll_Q3.csv` en el repo es un **DECOY** (flag falsa).
El payload REAL (con la flag verdadera) vive en el secret de GitHub Actions
`SILENT_HARVEST_PAYLOAD` y se inyecta en la imagen SOLO durante el build de CI
(`.github/workflows/release-silent-harvest.yml`). Así la flag nunca está en el
repositorio en claro. Los alumnos hacen `pull` de la imagen de GHCR (con el
payload real); los builds locales usan el decoy.

# runtime/portal — nota de mantenedor

`seed/auth_token.txt` en el repo es un **DECOY** (flag falsa). El token REAL
(con la flag verdadera) vive en el secret de GitHub Actions `PLAIN_SIGHT_TOKEN`
y se inyecta en la imagen SOLO durante el build de CI
(`.github/workflows/release-plain-sight.yml`). Así la flag nunca está en el
repositorio en claro. Los alumnos hacen `pull` de la imagen de GHCR (con el
token real); los builds locales usan el decoy.

# webserver — Drive By

Sitio de descargas malicioso que sirve un ejecutable por HTTP en claro. El PE
falso lleva la flag embebida (`payload-token:`), leída de `seed/payload_token.txt`.
En el repo es un **DECOY**; el token real se inyecta en CI desde `DRIVE_BY_TOKEN`.

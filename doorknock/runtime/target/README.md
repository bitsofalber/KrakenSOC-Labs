# target — Doorknock

Servidor con varios puertos abiertos. El panel de admin (8080) devuelve un banner
con la service-key (la flag), leída de `seed/service_key.txt`. En el repo es un
**DECOY**; el token real se inyecta en CI desde el secret `DOORKNOCK_TOKEN`.

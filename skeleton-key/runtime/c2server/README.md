# c2server — Skeleton Key

C2 sobre TLS con key exchange RSA (descifrable con la clave privada). El tasking
lleva la flag, leida de `seed/c2_token.txt`. En el repo es un **DECOY**; el token
real se inyecta en CI desde `SKELETON_KEY_TOKEN`.

server.key se publica A PROPOSITO (resources/decrypt-me.key): es el material que
el alumno carga en Wireshark para descifrar. La flag NO esta en la clave.

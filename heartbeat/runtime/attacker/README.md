# attacker — Heartbeat

Host comprometido que exfiltra un fichero confidencial por tunel ICMP (payloads
base64 en echo requests). La flag va en el fichero, leida de `seed/exfil_token.txt`.
En el repo es un **DECOY**; el token real se inyecta en CI desde `HEARTBEAT_TOKEN`.

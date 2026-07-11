# implant — Dark Water

Exfiltra un fichero por DoH: cada consulta /resolve?name= lleva un trozo base64url.
La flag va en el dato exfiltrado, leida de `seed/doh_token.txt`. En el repo es un
**DECOY**; el token real se inyecta en CI desde `DARK_WATER_TOKEN`.

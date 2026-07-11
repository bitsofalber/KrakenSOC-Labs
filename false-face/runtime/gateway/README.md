# gateway — False Face

Portal/gateway HTTP en claro que el atacante suplanta por ARP. Sirve la pagina
con la flag (`session_token`), leida de `seed/session_token.txt`. En el repo es
un **DECOY**; el token real se inyecta en CI desde `FALSE_FACE_TOKEN`.

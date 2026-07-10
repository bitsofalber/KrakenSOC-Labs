# telnetd — Open Line

Router core legacy administrado por Telnet en claro (puerto 23). Al ejecutar
`show running-config` vuelca la `service-key` (la flag) por la red.

La flag se lee de `seed/service_key.txt`. En el repo es un **DECOY**; la key real
se inyecta solo en CI desde el secret `OPEN_LINE_TOKEN`.

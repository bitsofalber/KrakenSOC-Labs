# Open Line — Cleartext Telnet Admin Session

> **Dificultad:** Principiante · **Familia:** Forense de Red · **Duración estimada:** ~30 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Northwind sigue administrando un **router core legacy** (`nw-core-rtr01`) por
**Telnet en claro** (puerto 23) en vez de SSH. Se capturó una sesión de
administración: un operador inicia sesión y ejecuta `show running-config`, con lo
que el equipo vuelca su configuración —incluida una **service-key**— legible por
la red.

Como analista, tienes la captura (`pcaps/telnet-cleartext.pcap`). Telnet no cifra
nada: credenciales y salida de comandos están a la vista.

## Objetivo

1. Identifica el protocolo y puerto de la sesión de administración.
2. Recupera el **usuario** y la **contraseña** del login.
3. Identifica el **comando** que vuelca la configuración.
4. Mapea la técnica de **MITRE ATT&CK**.
5. Recupera la **service-key** (la flag) del volcado de configuración.

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/open-line
./deploy.sh
```

- **Comprobar salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- En Wireshark, *Follow → TCP Stream* sobre la sesión reconstruye toda la
  conversación (login + comandos + salida) en una ventana.
- La service-key aparece en el volcado de `show running-config` como `service-key ...`.

Las respuestas se validan en **KrakenSOC** (server-side). Este repositorio no
contiene la solución en claro (ver `answers/`).

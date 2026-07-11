# Skeleton Key — Decryptable TLS C2

> **Dificultad:** Avanzado · **Familia:** Forense de Red · **Duración estimada:** ~50 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Un implante en Northwind se comunica con su C2 **por TLS** — parece opaco. Pero el
C2 está mal configurado: usa **intercambio de claves RSA** (sin forward secrecy)
en vez de ECDHE. El equipo de IR recuperó la **clave privada** del servidor
(`resources/decrypt-me.key`). Con ella se **descifra todo** el tráfico capturado.

Tienes la captura (`pcaps/tls-c2.pcap`) y la clave. Descifra el C2 y saca el
`decrypt_key` del tasking (la flag).

## Objetivo

1. Identifica el **protocolo/puerto** y la **versión** de TLS.
2. Reconoce el **key exchange RSA** (lo que lo hace descifrable).
3. Lee el **SNI** del ClientHello (sin descifrar).
4. Mapea la técnica de **MITRE ATT&CK**.
5. **Descifra** con la clave y recupera la flag del tasking.

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/skeleton-key
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Descifrar en Wireshark

1. Edit → Preferences → Protocols → **TLS** → *RSA keys list* → **+**.
2. Añade: IP del c2server, Port `443`, Protocol `http`, Key File `resources/decrypt-me.key`.
3. Aplica el filtro `http` o *Follow → HTTP Stream*: verás el tasking JSON en claro.
4. El campo `decrypt_key` es la flag.

> Con ECDHE (forward secrecy) esto NO sería posible: la clave privada no basta.
> El fallo aquí es usar RSA key exchange.

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

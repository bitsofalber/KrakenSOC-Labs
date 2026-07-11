# Heartbeat — ICMP Tunnel Exfiltration

> **Dificultad:** Intermedio · **Familia:** Forense de Red · **Duración estimada:** ~40 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Un host comprometido de Northwind exfiltra un documento confidencial **por un
túnel ICMP**: en vez de subirlo por HTTP/FTP (que un proxy vería), trocea el
fichero, lo codifica en base64 y saca un trozo en el **payload de cada ICMP echo
request** (ping). El ICMP suele estar permitido y poco inspeccionado.

Tienes la captura (`pcaps/icmp-tunnel.pcap`). Reensambla los payloads,
decodifícalos y recupera el fichero robado (con la flag).

## Objetivo

1. Identifica el **protocolo** del túnel (ICMP).
2. Mapea la técnica de **MITRE ATT&CK**.
3. Reconoce la **codificación** (base64).
4. Lee la **clasificación** y el **campo** del documento.
5. **Reensambla y decodifica** los payloads → la flag.

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/heartbeat
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- Los ICMP echo request normales llevan un payload de relleno fijo. Aquí llevan
  **datos** que cambian: filtra `icmp.type==8` y mira el campo *Data*.
- Ordena por `icmp.seq`, concatena los payloads y `base64 -d`.

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

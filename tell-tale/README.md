# Tell Tale — TLS JA3 Fingerprinting & Cert Analysis

> **Dificultad:** Avanzado · **Familia:** Forense de Red · **Duración estimada:** ~50 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Un implante en Northwind hace beacon a su C2 **por TLS**. No lo desciframos (hay
forward secrecy), pero **no hace falta**: el análisis se hace por **metadatos**.
El **ClientHello** del implante tiene un **JA3** distintivo que identifica la
herramienta, y el **certificado** del servidor viaja **en claro** en el handshake
— su Subject (campo **O**) lleva la flag.

Tienes la captura (`pcaps/tls-ja3.pcap`). Huellea el cliente y extrae el secreto
del certificado, sin descifrar nada.

## Objetivo

1. Identifica el **protocolo/puerto** y el **SNI**.
2. Calcula el **JA3** del ClientHello (identifica la herramienta).
3. Localiza el **campo del Subject** que filtra el secreto.
4. Mapea la técnica de **MITRE ATT&CK**.
5. **Extrae el certificado** y recupera el campo O (la flag).

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/tell-tale
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- El SNI y el **certificado** van en claro en el handshake TLS 1.2 (aunque el
  resto se cifre). En Wireshark: `tls.handshake.type==11` (Certificate).
- El **JA3** es un hash del ClientHello (versión, ciphers, extensiones…). Con el
  plugin JA3 de Wireshark o `pyja3` lo obtienes.
- El campo **O** (Organization) del Subject del certificado es la flag.

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

# Dark Water — DNS-over-HTTPS (DoH) Exfiltration

> **Dificultad:** Avanzado · **Familia:** Forense de Red · **Duración estimada:** ~55 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Un host comprometido de Northwind exfiltra datos por **DoH (DNS-over-HTTPS)**.
Cada consulta `/resolve?name=<chunk>.exfil.n0rthwind-doh.com` lleva un trozo del
dato en base64url, **dentro de HTTPS** — así el proxy DNS de la empresa no lo ve.
El C2 usa TLS con **key exchange RSA**, y el IR recuperó la clave privada
(`resources/decrypt-me.key`).

Tienes la captura (`pcaps/doh-exfil.pcap`) y la clave. Descifra, reensambla las
consultas y recupera el secreto.

## Objetivo

1. Reconoce el canal (**DoH**) y el **resolver** (SNI).
2. Mapea la técnica de **MITRE ATT&CK** (tunneling).
3. **Descifra** el TLS con la clave.
4. Reensambla el parámetro **?name=** de cada consulta.
5. **Decodifica** (base64url) y recupera el **vpn_token** (la flag).

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/dark-water
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- El SNI `dns.n0rthwind-doh.com` (typosquat) delata un resolver DoH no autorizado.
- Descifra el TLS con `resources/decrypt-me.key` (RSA key exchange, sin forward secrecy).
- Los `?name=` llevan `<base64url>.sNN.exfil...`: ordena por `sNN`, concatena y `base64 -d`.

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

# Relay Race — SMB/NTLM Capture

> **Dificultad:** Intermedio · **Familia:** Forense de Red · **Duración estimada:** ~45 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Un empleado de Northwind accede al **share SMB de Finanzas** autenticándose con
**NTLM**. En el handshake NTLMSSP viajan el usuario, el dominio y la respuesta
NTLMv2 (el "hash" que un atacante capturaría para crackear o hacer relay). Y el
fichero al que accede —sin cifrado SMB— también queda legible.

Tienes la captura (`pcaps/smb-ntlm.pcap`). Extrae la identidad del handshake y
recupera el secreto del fichero.

## Objetivo

1. Identifica el **protocolo/puerto** (SMB / 445).
2. Recupera **usuario** y **dominio** del handshake NTLMSSP.
3. Identifica el **mecanismo** de autenticación (NTLM).
4. Mapea la técnica de **MITRE ATT&CK**.
5. Sigue el read del fichero y recupera el **vault_token** (la flag).

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/relay-race
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- Filtro `ntlmssp` en Wireshark → el mensaje NTLMSSP_AUTH trae el usuario, el
  dominio y la respuesta NTLMv2. Wireshark te lo desglosa.
- Filtro `smb2` y sigue el read de Payroll_Q4_2026.txt para el vault_token.

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

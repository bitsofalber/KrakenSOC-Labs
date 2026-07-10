# Carbon Copy — Cleartext SMTP Phishing

> **Dificultad:** Principiante · **Familia:** Forense de Red · **Duración estimada:** ~35 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Northwind usa un **relay SMTP interno legacy** que acepta correo **sin cifrar**
(puerto 25, sin STARTTLS). Un **correo de phishing** con un adjunto malicioso pasa
por el relay hacia un empleado. Como el SMTP va en claro, todo el mensaje
—remitente, destinatario, asunto y adjunto— queda legible en la captura.

Tienes el PCAP (`pcaps/smtp-cleartext.pcap`). Reconstruye el correo y decodifica
el adjunto (base64) para sacar el token embebido (la flag).

## Objetivo

1. Identifica el protocolo y puerto del correo.
2. Recupera el **remitente** (MAIL FROM) y el **destinatario** (RCPT TO).
3. Lee el **asunto**.
4. Mapea la técnica de **MITRE ATT&CK** del phishing con adjunto.
5. **Decodifica el adjunto base64** y recupera el token (la flag).

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/carbon-copy
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- En Wireshark, *Follow → TCP Stream* de la sesión SMTP muestra los comandos
  (MAIL FROM, RCPT TO, DATA) y el mensaje completo, incluido el adjunto base64.
- El adjunto va tras `Content-Transfer-Encoding: base64`. Cópialo y decodifícalo
  (`base64 -d`): la flag está embebida como `verification-token`.

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

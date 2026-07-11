# Full Circle — Multi-Stage Kill Chain (Capstone)

> **Dificultad:** Avanzado · **Familia:** Forense de Red · **Duración estimada:** ~60 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

El **capstone** de forense de red: un ataque completo en una sola captura. Un
atacante contra un servidor interno de Northwind ejecuta el kill chain de punta a
punta:

1. **Recon** — escanea los puertos del servidor.
2. **Credential Access** — inicia sesión en el portal por HTTP en claro con una
   cuenta de servicio.
3. **Exfiltration** — con la sesión, descarga un export sensible de nóminas.

Tienes la captura (`pcaps/kill-chain.pcap`). Reconstruye las 3 fases y recupera
la flag del fichero exfiltrado.

## Objetivo

1. Reconoce la fase de **reconocimiento**.
2. Recupera **usuario** y **contraseña** del login.
3. Identifica el **fichero exfiltrado**.
4. Mapea las fases a **MITRE ATT&CK**.
5. Reconstruye el export y recupera el **export_token** (la flag).

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/full-circle
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- Sigue el **orden temporal**: primero muchas conexiones cortas (scan), luego
  `POST /login` (creds en claro), luego `GET /admin/export.csv` con la cookie SID.
- El `export_token` está en el CSV descargado (Follow HTTP Stream o Export Objects).

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

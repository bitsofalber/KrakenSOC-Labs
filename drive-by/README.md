# Drive By — Cleartext HTTP Malware Download

> **Dificultad:** Principiante · **Familia:** Forense de Red · **Duración estimada:** ~35 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Un empleado de Northwind visita un **sitio de descargas typosquat**
(`cdn.northw1nd-files.com`) por **HTTP en claro** y se baja un "Invoice Viewer"
que en realidad es un **ejecutable malicioso**. Como la descarga va sin cifrar,
el binario completo queda capturado y es reconstruible del PCAP.

Tienes la captura (`pcaps/http-malware.pcap`). Extrae el binario, identifícalo y
saca el token embebido (la flag).

## Objetivo

1. Identifica el protocolo y puerto de la descarga.
2. Identifica el **host** (dominio) y el **nombre de fichero**.
3. Reconoce el fichero como **ejecutable** por su magic (MZ).
4. Mapea la técnica de **MITRE ATT&CK**.
5. **Extrae el binario** (Export Objects) y recupera el token (la flag).

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/drive-by
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- En Wireshark: *File → Export Objects → HTTP*, guarda el .exe.
- `file Invoice_Viewer_Setup.exe` → empieza por `MZ` (ejecutable Windows).
- `strings Invoice_Viewer_Setup.exe | grep NORTHWIND` → la flag (`payload-token`).

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

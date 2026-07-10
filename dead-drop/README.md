# Dead Drop — Cleartext FTP Credential & File Exfiltration

> **Dificultad:** Principiante · **Familia:** Forense de Red · **Duración estimada:** ~35 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Northwind Global Systems mantiene un servidor FTP interno para el intercambio de
ficheros del equipo de Sales — el *Sales File Drop*. Nunca se migró a SFTP/FTPS:
sigue sirviendo por **FTP en claro** (puerto 21). Alguien ha usado una **cuenta de
servicio válida** para entrar y descargarse un **export de clientes confidencial**.

Como analista, tienes la **captura de red** (`pcaps/ftp-cleartext.pcap`). No hay
malware ni exploit: el fallo es el protocolo sin cifrar. Todo lo que necesitas
está legible en el PCAP — solo hay que saber leerlo.

## Objetivo

A partir de la captura:

1. Identifica el protocolo y puerto que transportan las credenciales.
2. Recupera el **usuario** y la **contraseña** del canal de control (`USER` / `PASS`).
3. Identifica el **fichero exfiltrado** (`RETR`).
4. Mapea la técnica de **MITRE ATT&CK** de exfiltración sobre protocolo sin cifrar.
5. **Reconstruye el fichero** del canal de datos y recupera el **token de exportación** (la flag).

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/dead-drop
./deploy.sh
```

`deploy.sh` levanta 3 contenedores (servidor FTP, estación que descarga, sniffer),
genera la captura en `pcaps/ftp-cleartext.pcap` y la deja lista para analizar.

- **Comprobar salud:** `./verify.sh`
- **Reiniciar la captura:** `./reset.sh`
- **Apagar y limpiar:** `./destroy.sh`

## Pistas de análisis

- FTP separa **canal de control** (puerto 21: comandos `USER`, `PASS`, `RETR`…) del
  **canal de datos** (puertos pasivos: el contenido de los ficheros).
- En Wireshark: `Follow → TCP Stream` sobre el control para leer los comandos, y
  sobre el flujo de datos para reconstruir el fichero. `File → Export Objects → FTP-DATA`
  también sirve.
- La flag va embebida al final del fichero exfiltrado, como `export_token`.

Las respuestas se validan en **KrakenSOC** (server-side). Este repositorio no
contiene la solución en claro (ver `answers/`).

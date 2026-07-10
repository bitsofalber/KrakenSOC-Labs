# Doorknock — Nmap Port Scan Analysis

> **Dificultad:** Intermedio · **Familia:** Forense de Red · **Duración estimada:** ~40 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Un atacante en la red de Northwind lanza un **escaneo de puertos (Nmap)** contra
un servidor interno para descubrir sus servicios. El escaneo queda capturado. Uno
de los servicios —el **panel de administración en el puerto 8080**— devuelve un
banner con una **service-key**.

Tienes la captura (`pcaps/nmap-scan.pcap`). Reconstruye qué puertos están abiertos
y saca el secreto del banner.

## Objetivo

1. Reconoce la actividad como un **escaneo de puertos**.
2. Cuenta cuántos puertos responden **abiertos** (SYN-ACK).
3. Identifica el **puerto** del panel de admin y su **banner**.
4. Mapea la técnica de **MITRE ATT&CK**.
5. Recupera la **service-key** del banner (la flag).

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/doorknock
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- Un escaneo se ve como muchos SYN a puertos distintos. Los **abiertos** responden
  SYN-ACK; los **cerrados**, RST.
- Filtro Wireshark para puertos abiertos: `tcp.flags.syn==1 && tcp.flags.ack==1`.
- El banner del 8080 (Follow TCP Stream) lleva `service-key=...`.

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

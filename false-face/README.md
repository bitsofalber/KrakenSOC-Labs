# False Face — ARP Spoofing / MITM

> **Dificultad:** Intermedio · **Familia:** Forense de Red · **Duración estimada:** ~45 min
> **Canon:** Northwind Global Systems · **Flag:** 1 (`NORTHWIND{...}`)

## Escenario

Un atacante en la LAN de Northwind **envenena la caché ARP**: manda ARP replies
diciendo que la IP del gateway es suya. Los hosts del segmento le empiezan a
enviar el tráfico del gateway (un **MITM** clásico). La víctima navega al portal
interno por HTTP en claro y su tráfico —con un **session_token**— queda expuesto.

Tienes la captura (`pcaps/arp-mitm.pcap`). Detecta el envenenamiento ARP y
recupera el secreto del HTTP interceptado.

## Objetivo

1. Reconoce el **ataque** (ARP spoofing / poisoning).
2. Mapea la técnica de **MITRE ATT&CK**.
3. Detecta la **MAC duplicada** para la IP del gateway.
4. Identifica el **protocolo** y la **ruta** interceptados.
5. Recupera el **session_token** (la flag).

## Cómo desplegarlo

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/false-face
./deploy.sh
```

- **Salud:** `./verify.sh` · **Reiniciar:** `./reset.sh` · **Limpiar:** `./destroy.sh`

## Pistas

- Filtro `arp` en Wireshark: verás muchos ARP *reply* (is-at) diciendo que la IP
  del gateway está en la MAC del atacante. Wireshark marca "duplicate use of IP".
- Filtro `http`: sigue el `GET /admin` y lee el `session_token` de la respuesta.

Las respuestas se validan en **KrakenSOC** (server-side). Sin solución en claro (ver `answers/`).

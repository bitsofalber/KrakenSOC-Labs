# Changelog — Heartbeat

## 1.0.0
- Lab inicial: forense de red sobre exfiltracion por tunel ICMP (Intermedio).
- Escenario Northwind: un host comprometido saca un documento confidencial en
  payloads base64 de ICMP echo requests.
- 3 contenedores: host (destino ICMP), attacker (scapy, exfil), sniffer.
- 6 preguntas (protocolo, tecnica, codificacion, clasificacion, campo, flag).
- Evidencia: pcaps/icmp-tunnel.pcap.

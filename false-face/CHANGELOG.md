# Changelog — False Face

## 1.0.0
- Lab inicial: forense de red sobre ARP spoofing / MITM (Intermedio).
- Escenario Northwind: un atacante envenena la cache ARP para hacer MITM; la
  victima navega en claro y su session_token queda capturado.
- 4 contenedores: gateway (portal HTTP), victim, attacker (scapy ARP), sniffer.
- 6 preguntas (ataque, tecnica, MAC duplicada, protocolo, ruta, flag).
- Evidencia: pcaps/arp-mitm.pcap.

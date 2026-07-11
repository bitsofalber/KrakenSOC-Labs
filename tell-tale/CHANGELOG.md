# Changelog — Tell Tale

## 1.0.0
- Lab inicial: JA3 fingerprinting + analisis de certificado TLS (Avanzado).
- Escenario Northwind: C2 sobre TLS; se identifica el implante por su JA3 y se
  extrae la flag del Subject del certificado (que viaja en claro).
- 3 contenedores: c2server (TLS 1.2, cert con la flag), implant (JA3), sniffer.
- 6 preguntas (protocolo, SNI, JA3, campo Subject, tecnica ATT&CK, flag).
- Evidencia: pcaps/tls-ja3.pcap.

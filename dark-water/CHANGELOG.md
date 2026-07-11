# Changelog — Dark Water

## 1.0.0
- Lab inicial: exfiltracion por DNS-over-HTTPS (DoH) (Avanzado).
- Escenario Northwind: un implante exfiltra por DoH sobre TLS descifrable; el IR
  descifra, reensambla las consultas y recupera el dato.
- 3 contenedores: doh-server (TLS RSA), implant (exfil DoH), sniffer.
- 6 preguntas (canal, SNI, tecnica, parametro, codificacion, flag).
- Evidencia: pcaps/doh-exfil.pcap + resources/decrypt-me.key.

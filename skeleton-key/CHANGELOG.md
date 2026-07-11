# Changelog — Skeleton Key

## 1.0.0
- Lab inicial: descifrado de C2 sobre TLS (Avanzado).
- Escenario Northwind: C2 con key exchange RSA (sin forward secrecy); el IR
  recupera la clave privada y descifra el tasking (con la flag).
- 3 contenedores: c2server (TLS RSA), implant (beacon), sniffer.
- 6 preguntas (protocolo, version, key exchange, SNI, tecnica ATT&CK, flag).
- Evidencia: pcaps/tls-c2.pcap + resources/decrypt-me.key.

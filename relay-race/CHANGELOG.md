# Changelog — Relay Race

## 1.0.0
- Lab inicial: forense de red sobre SMB/NTLM (Intermedio).
- Escenario Northwind: un empleado accede al share de Finanzas por SMB con NTLM;
  el handshake NTLMSSP y el fichero (sin cifrar) quedan capturados.
- 3 contenedores: smbserver (impacket), client (impacket NTLM), sniffer.
- 6 preguntas (protocolo, usuario, dominio, auth, tecnica ATT&CK, flag).
- Evidencia: pcaps/smb-ntlm.pcap.

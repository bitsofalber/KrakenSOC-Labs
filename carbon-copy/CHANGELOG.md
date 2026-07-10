# Changelog — Carbon Copy

## 1.0.0
- Lab inicial: forense de red sobre SMTP en claro (Principiante).
- Escenario Northwind: phishing con adjunto por un relay SMTP sin cifrar; el
  correo entero (cabeceras + adjunto base64 con la flag) viaja legible.
- 3 contenedores: smtpd (relay legacy), workstation (envia el phishing), sniffer.
- 6 preguntas (protocolo, remitente, destinatario, asunto, tecnica ATT&CK, flag).
- Evidencia: pcaps/smtp-cleartext.pcap.

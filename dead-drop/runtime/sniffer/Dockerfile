FROM alpine:3.20
RUN apk add --no-cache tcpdump
# Captura el canal de control FTP (21) y el rango pasivo de datos -> evidencia.
CMD ["sh", "-c", "tcpdump -i any -U -w /pcaps/ftp-cleartext.pcap 'tcp port 21 or tcp portrange 30000-30009'"]

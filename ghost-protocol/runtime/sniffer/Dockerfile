FROM alpine:3.20
RUN apk add --no-cache tcpdump
# Captura el HTTP (puerto 80) que llega al C2 por su interfaz de red (eth0).
# Usamos eth0 en vez de "any" para no capturar cada trama por duplicado, así el
# recuento de beacons en el PCAP es exacto. Los health-checks van por loopback
# y no ensucian la evidencia.
CMD ["sh", "-c", "tcpdump -i eth0 -U -w /pcaps/ghost-protocol.pcap tcp port 80"]

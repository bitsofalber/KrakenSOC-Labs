FROM alpine:3.20
RUN apk add --no-cache tcpdump
CMD ["sh", "-c", "tcpdump -i any -U -w /pcaps/arp-mitm.pcap arp or tcp port 80"]

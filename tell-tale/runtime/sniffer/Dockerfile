FROM alpine:3.20
RUN apk add --no-cache tcpdump
CMD ["sh", "-c", "tcpdump -i any -U -w /pcaps/tls-ja3.pcap tcp port 443"]

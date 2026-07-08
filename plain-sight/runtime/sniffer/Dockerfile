FROM alpine:3.20
RUN apk add --no-cache tcpdump
# Captura TODO el HTTP (puerto 80) que llega al portal -> evidencia del alumno.
CMD ["sh", "-c", "tcpdump -i any -U -w /pcaps/cleartext-http.pcap tcp port 80"]

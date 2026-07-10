FROM alpine:3.20
RUN apk add --no-cache nmap netcat-openbsd
WORKDIR /app
COPY run.sh .
RUN chmod +x run.sh
CMD ["./run.sh"]

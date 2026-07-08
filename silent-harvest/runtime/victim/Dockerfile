FROM python:3.12-slim
RUN pip install --no-cache-dir dnslib==0.9.24
WORKDIR /app
COPY exfil.py .
COPY seed/ /seed/
# Ejecuta la exfiltración una vez y mantiene el contenedor vivo (para verify.sh)
CMD ["sh", "-c", "python exfil.py; touch /tmp/exfil_done; tail -f /dev/null"]

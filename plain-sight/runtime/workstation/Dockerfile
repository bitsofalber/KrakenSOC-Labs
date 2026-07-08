FROM python:3.12-slim
WORKDIR /app
COPY client.py .
# Ejecuta el flujo una vez y mantiene el contenedor vivo (para verify.sh).
CMD ["sh", "-c", "python client.py; touch /tmp/session_done; tail -f /dev/null"]

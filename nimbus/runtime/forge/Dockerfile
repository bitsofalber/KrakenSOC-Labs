FROM python:3.12-slim
WORKDIR /app
COPY forge.py .
COPY seed/ /seed/
# Genera el dataset e ingesta por HEC; luego se mantiene vivo (para verify.sh).
CMD ["sh", "-c", "python forge.py && tail -f /dev/null"]

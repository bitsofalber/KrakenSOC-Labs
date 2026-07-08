FROM python:3.12-slim
WORKDIR /app
COPY implant.py .
COPY seed/ /seed/
# Ejecuta la campaña una vez y mantiene vivo el contenedor (para verify.sh).
CMD ["sh", "-c", "python implant.py; touch /tmp/implant_done; tail -f /dev/null"]

FROM python:3.12-slim
WORKDIR /app
COPY server.py .
COPY seed/ /seed/
EXPOSE 80
# Portal HTTP en claro; solo stdlib, sin dependencias.
CMD ["python", "server.py"]

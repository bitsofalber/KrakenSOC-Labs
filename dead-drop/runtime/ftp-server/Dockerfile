FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir pyftpdlib==1.5.10
COPY server.py .
COPY seed/ /seed/
EXPOSE 21 30000-30009
# Servidor FTP en claro. La flag real se inyecta en /seed en el build de CI.
CMD ["python", "server.py"]

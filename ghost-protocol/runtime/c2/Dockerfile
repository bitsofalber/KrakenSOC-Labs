FROM python:3.12-slim
WORKDIR /app
COPY server.py .
EXPOSE 80
# Team Server HTTP; solo stdlib, sin dependencias. No lleva el fichero robado:
# ese vive en la víctima (implant); el C2 solo conoce la RUTA a tasquear.
CMD ["python", "server.py"]

FROM python:3.12-slim
WORKDIR /app
COPY server.py server.crt server.key ./
EXPOSE 443
CMD ["python", "server.py"]

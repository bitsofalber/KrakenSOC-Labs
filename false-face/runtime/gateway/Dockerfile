FROM python:3.12-slim
WORKDIR /app
COPY server.py .
COPY seed/ /seed/
EXPOSE 80
CMD ["python", "server.py"]

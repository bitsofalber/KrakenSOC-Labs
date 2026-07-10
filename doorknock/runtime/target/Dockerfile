FROM python:3.12-slim
WORKDIR /app
COPY server.py .
COPY seed/ /seed/
EXPOSE 22 80 443 3306 8080
CMD ["python", "server.py"]

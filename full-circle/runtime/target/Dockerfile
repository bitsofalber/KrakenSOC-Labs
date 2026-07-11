FROM python:3.12-slim
WORKDIR /app
COPY server.py .
COPY seed/ /seed/
EXPOSE 22 80 3306
CMD ["python", "server.py"]

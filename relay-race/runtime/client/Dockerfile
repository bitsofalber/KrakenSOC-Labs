FROM python:3.12-slim
RUN pip install --no-cache-dir impacket==0.11.0
WORKDIR /app
COPY client.py .
CMD ["python", "client.py"]

FROM python:3.12-slim
RUN pip install --no-cache-dir impacket==0.11.0
WORKDIR /app
COPY server.py .
COPY seed/ /seed/
EXPOSE 445
CMD ["python", "server.py"]

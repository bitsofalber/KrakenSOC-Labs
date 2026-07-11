FROM python:3.12-slim
RUN pip install --no-cache-dir scapy==2.5.0
WORKDIR /app
COPY spoof.py .
CMD ["python", "spoof.py"]

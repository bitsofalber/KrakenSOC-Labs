FROM python:3.12-slim
RUN pip install --no-cache-dir dnslib==0.9.24
WORKDIR /app
COPY resolver.py .
EXPOSE 53/udp
CMD ["python", "resolver.py"]

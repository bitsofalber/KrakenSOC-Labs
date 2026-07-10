FROM python:3.12-slim
WORKDIR /app
COPY client.py .
CMD ["sh", "-c", "python client.py; touch /tmp/session_done; tail -f /dev/null"]

FROM python:3.12-slim
WORKDIR /app
COPY apps/telegram-gateway/pyproject.toml ./
RUN pip install --no-cache-dir .
COPY packages /app/packages
COPY apps/telegram-gateway/src /app/src
ENV PYTHONPATH=/app:/app/src
CMD ["uvicorn","src.main:app","--host","127.0.0.1","--port","8082"]

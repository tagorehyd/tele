FROM python:3.12-slim
WORKDIR /app
COPY apps/upload-manager/pyproject.toml ./
RUN pip install --no-cache-dir . pytest pytest-asyncio
COPY packages /app/packages
COPY apps/upload-manager/src /app/src
ENV PYTHONPATH=/app:/app/src
CMD ["uvicorn","src.main:app","--host","127.0.0.1","--port","8081"]

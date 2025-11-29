FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p media_output

CMD ["sh", "-c", "celery -A app.celery_app worker --loglevel=info --concurrency=1 --max-tasks-per-child=1 & uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
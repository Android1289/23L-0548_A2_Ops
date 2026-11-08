# VisionGuard Web Application Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    TF_ENABLE_ONEDNN_OPTS=0 \
    MALLOC_TRIM_THRESHOLD_=100000 \
    MODEL_PATH=/app/models/champion/visionguard.keras \
    DATABASE_URL=sqlite:////tmp/visionguard.db

WORKDIR /app

# 1) Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Unprivileged user
RUN useradd --create-home --uid 10001 appuser

# 3) Source code and baked champion model
COPY serving/ serving/
COPY webapp/ webapp/
COPY models/ models/
COPY app.py app.py

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000 7860 10000

# Bind dynamically to whatever $PORT cloud assigns (Render=10000, HF=7860, Local=5000)
# Single thread and 1 worker ensures RAM stays under 400 MB (Render free tier limit is 512 MB)
CMD ["sh", "-c", "gunicorn -w 1 --threads 1 --timeout 180 -b 0.0.0.0:${PORT:-10000} app:app"]

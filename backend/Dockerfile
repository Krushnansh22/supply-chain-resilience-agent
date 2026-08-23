# ==============================================================
# backend/Dockerfile
# Supply Chain Resilience Agent — Backend API Container
# ==============================================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# System dependencies:
# - curl: needed for container healthcheck
# - sqlite3: utility for local inspection if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies with pip caching optimization
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and seed data
COPY app ./app
COPY seed_data ./seed_data

# Create data directory for local artifacts or file storage
RUN mkdir -p /app/data

EXPOSE 8000

# Container healthcheck testing /health endpoint
HEALTHCHECK --interval=15s --timeout=5s --retries=5 --start-period=15s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

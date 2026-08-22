# ==============================================================
# backend/Dockerfile
# Owner: Developer 2 (Backend / Simulation)
# ==============================================================
FROM python:3.11-slim

WORKDIR /app

# System deps (sqlite3 CLI is handy for debugging during the hackathon)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# SQLite file lives here; mounted as a docker volume in docker-compose.yml
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

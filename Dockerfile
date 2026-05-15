# ── Stage 1: Build React frontend ──────────────────────────────
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python runtime ─────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bring in built frontend
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Orchestrator serves both API and frontend on port 8000
EXPOSE 8000

RUN mkdir -p /var/log/supervisor

RUN printf '#!/bin/bash\n\
set -e\n\
echo "GROQ_API_KEY=${GROQ_API_KEY}" > /app/.env\n\
echo "TAVILY_API_KEY=${TAVILY_API_KEY}" >> /app/.env\n\
echo "DEMO_MODE=${DEMO_MODE:-false}" >> /app/.env\n\
echo "Starting Travel Planner services..."\n\
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf\n\
' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]

# Made with Bob

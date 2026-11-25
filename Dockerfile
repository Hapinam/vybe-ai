# One Azure Container App serves both the FastAPI endpoints and the React UI.
FROM node:22-alpine@sha256:1314fb30ec37592d5845e5a160d522c0e680972aa534549940b8d73bde88481a AS web
WORKDIR /build
COPY apps/web/package*.json ./
RUN npm ci --no-audit --no-fund
COPY apps/web/ ./
RUN npm run build

FROM python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app
COPY apps/api/ /app/api/
RUN apt-get update && \
    apt-get install --only-upgrade -y zlib1g libzstd1 && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --require-hashes -r /app/api/requirements.lock && pip install --no-cache-dir --no-deps /app/api && \
    pip uninstall -y setuptools wheel && \
    useradd --create-home --uid 10001 appuser
COPY --from=web /build/dist/ /app/static/
USER appuser
EXPOSE 8000
CMD ["uvicorn", "vybe.deployed:app", "--app-dir", "/app/api", "--host", "0.0.0.0", "--port", "8000"]

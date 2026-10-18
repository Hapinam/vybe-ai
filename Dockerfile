# One Azure Container App serves both the FastAPI endpoints and the React UI.
FROM node:22-alpine AS web
WORKDIR /build
COPY apps/web/package*.json ./
RUN npm ci --no-audit --no-fund
COPY apps/web/ ./
RUN npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app
COPY apps/api/ /app/api/
RUN pip install --no-cache-dir /app/api && \
    pip install --no-cache-dir --upgrade 'jaraco.context>=6.1.0' 'wheel>=0.46.2' && \
    useradd --create-home --uid 10001 appuser
COPY --from=web /build/dist/ /app/static/
USER appuser
EXPOSE 8000
CMD ["uvicorn", "vybe.deployed:app", "--app-dir", "/app/api", "--host", "0.0.0.0", "--port", "8000"]

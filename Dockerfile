# ==========================================
# Backend Dockerfile - Multi-stage build
# ==========================================

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python en un directorio aislado
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Argumentos de build
ARG ENVIRONMENT=production

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH=/root/.local/bin:$PATH \
    ENVIRONMENT=${ENVIRONMENT}

WORKDIR /app

# Instalar solo runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

# Cambiar a usuario no-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]

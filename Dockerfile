# Imagen base
FROM python:3.11-slim

# Evitar buffering y forzar UTF-8
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema (ajusta si no necesitas todas)
RUN apt-get update && apt-get install -y \
    postgresql-client libpq5 curl \
 && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY . .

# 🔴 IMPORTANTE: ajustar el módulo de tu app aquí
#   si tu aplicación está en main.py con la variable app = FastAPI()
#   y ese main.py está en la raíz de /backend, entonces:
#       "main:app"
#   si está en una carpeta app/main.py → "app.main:app"
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

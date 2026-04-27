FROM python:3.11-slim

WORKDIR /app

# Copio requirements primero para aprovechar el cache de capas de Docker
# Si no cambia requirements.txt, Docker no reinstala dependencias en cada build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data

EXPOSE 8000

CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

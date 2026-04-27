# E-commerce Chat AI

API REST de e-commerce de zapatos con chat inteligente usando Clean Architecture y Google Gemini AI.

**Universidad EAFIT — Arquitectura de Software**

## Tecnologías

| Tecnología | Propósito |
|---|---|
| FastAPI | Framework HTTP para los endpoints |
| SQLAlchemy | ORM para SQLite |
| Pydantic | Validación de datos en DTOs |
| Google Gemini | Modelo de IA para el chat |
| Docker | Containerización |
| Pytest | Tests unitarios |

## Arquitectura

El proyecto usa Clean Architecture con 3 capas:

```
src/
├── domain/           # Entidades y reglas de negocio (sin dependencias externas)
├── application/      # Casos de uso, servicios y DTOs
└── infrastructure/   # FastAPI, SQLAlchemy, Gemini API
```

La regla fundamental es que las dependencias solo apuntan hacia adentro:
`Infrastructure → Application → Domain`. El dominio no sabe nada de FastAPI ni de SQLite.

## Requisitos previos

- Python 3.11+
- Docker y Docker Compose
- API Key de Google Gemini (obtener en https://aistudio.google.com/app/apikey)

## Instalación y ejecución

### Con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd e-commerce-chat-ai

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY

# 3. Construir y levantar
docker-compose up --build
```

### Sin Docker

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate    # Windows

pip install -r requirements.txt

cp .env.example .env
# Editar .env con tu GEMINI_API_KEY

uvicorn src.infrastructure.api.main:app --reload
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Info de la API |
| GET | `/health` | Health check |
| GET | `/products` | Listar todos los productos |
| GET | `/products/{id}` | Buscar producto por ID |
| POST | `/chat` | Enviar mensaje al asistente |
| GET | `/chat/history/{session_id}` | Historial de una sesión |
| DELETE | `/chat/history/{session_id}` | Limpiar historial |

### Documentación interactiva

Con la app corriendo, entra a http://localhost:8000/docs para ver y probar todos los endpoints en Swagger UI.

### Ejemplo de uso del chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "usuario1", "message": "Busco zapatos Nike para correr talla 42"}'
```

Respuesta:
```json
{
  "session_id": "usuario1",
  "user_message": "Busco zapatos Nike para correr talla 42",
  "assistant_message": "Tengo el Air Zoom Pegasus 40 de Nike en talla 42 por $120, con 5 unidades disponibles. Es ideal para running con amortiguación de aire reactiva. ¿Te interesa?",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Tests

```bash
pytest
pytest --tb=short -v   # con detalle
```

## Estructura completa

```
e-commerce-chat-ai/
├── src/
│   ├── config.py
│   ├── domain/
│   │   ├── entities.py       # Product, ChatMessage, ChatContext
│   │   ├── repositories.py   # Interfaces IProductRepository, IChatRepository
│   │   └── exceptions.py     # Excepciones de negocio
│   ├── application/
│   │   ├── dtos.py           # DTOs con validación Pydantic
│   │   ├── product_service.py
│   │   └── chat_service.py
│   └── infrastructure/
│       ├── api/main.py       # Endpoints FastAPI
│       ├── db/               # SQLAlchemy models, database setup, init data
│       ├── repositories/     # Implementaciones SQL de los repositorios
│       └── llm_providers/    # Integración con Gemini AI
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Autor

Sebastian Acosta Molina — Universidad EAFIT

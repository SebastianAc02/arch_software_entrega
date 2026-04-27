# E-commerce Chat AI

API REST de e-commerce de zapatos con chat inteligente, construida como ejercicio de Clean Architecture para el curso de Arquitectura de Software (SI3001) en la Universidad EAFIT.

La idea fue simple: una tienda de zapatos donde puedes consultar el catálogo por endpoints normales, pero también chatear con un asistente de IA que conoce el inventario y recuerda lo que dijiste antes.

**Universidad EAFIT — Arquitectura de Software**  
**Autor:** Sebastian Acosta Molina

---

## Tecnologías

| Tecnología | Para qué se usa |
|---|---|
| FastAPI | Los endpoints HTTP |
| SQLAlchemy | ORM sobre SQLite |
| Pydantic | Validación de datos en los DTOs |
| Google Gemini | El modelo de IA que genera las respuestas del chat |
| Docker | Containerización |
| Pytest | Tests unitarios |

---

## Arquitectura

El proyecto sigue Clean Architecture con 3 capas. La regla que traté de no romper nunca: **las dependencias solo apuntan hacia adentro**.

```
src/
├── domain/          # Entidades puras: Product, ChatMessage, ChatContext
│                    # No importa nada de FastAPI ni SQLAlchemy
├── application/     # Servicios que orquestan los casos de uso
│                    # Solo conoce el dominio, no sabe de HTTP ni de SQLite
└── infrastructure/  # FastAPI, SQLAlchemy, Gemini API
                     # Implementa las interfaces del dominio
```

### Por qué estas decisiones

**¿Por qué llamar a Gemini ANTES de guardar los mensajes?**  
Si la IA falla (timeout, límite de API, etc.), no quiero dejar un mensaje del usuario sin respuesta guardado en la base de datos. Primero confirmo que tengo respuesta, después persisto los dos mensajes.

**¿Por qué limitar el contexto a 6 mensajes?**  
Incluir toda la conversación en el prompt hace que crezca con cada mensaje. Con 6 mensajes tengo suficiente contexto para que la IA sea coherente, sin que el prompt se vuelva enorme y lento.

**¿Por qué interfaces en el dominio si solo uso SQLite?**  
Porque los tests unitarios las necesitan — puedo pasar un mock en lugar del repositorio real y testear la lógica del servicio sin tocar la base de datos. Lo entendí cuando quise testear `ChatService` sin tener que levantar SQLite.

**¿Por qué los productos se pasan completos a Gemini en cada request?**  
Porque el catálogo es pequeño (10 productos) y así la IA siempre tiene el inventario actualizado. Si el catálogo fuera grande habría que filtrar antes de armar el prompt.

---

## Instalación y ejecución

### Con Docker (recomendado)

```bash
git clone https://github.com/SebastianAc02/arch_software_entrega.git
cd arch_software_entrega

cp .env.example .env
# Editar .env y poner tu GEMINI_API_KEY

docker-compose up --build
```

La API queda disponible en http://localhost:8000

### Sin Docker

```bash
python3.11 -m venv venv
source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Editar .env con tu GEMINI_API_KEY

uvicorn src.infrastructure.api.main:app --reload
```

### Variables de entorno necesarias

```bash
GEMINI_API_KEY=tu_api_key_aqui          # Obtener en aistudio.google.com
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
```

---

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Info básica de la API |
| GET | `/health` | Verificar que está corriendo |
| GET | `/products` | Listar todos los productos |
| GET | `/products/{id}` | Buscar producto por ID |
| POST | `/chat` | Enviar mensaje al asistente |
| GET | `/chat/history/{session_id}` | Ver historial de una sesión |
| DELETE | `/chat/history/{session_id}` | Borrar historial |

Documentación interactiva disponible en http://localhost:8000/docs

### Ejemplo de uso del chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "usuario1", "message": "Busco zapatos Nike para correr talla 42"}'
```

Respuesta real del sistema:
```json
{
  "session_id": "usuario1",
  "user_message": "Busco zapatos Nike para correr talla 42",
  "assistant_message": "¡Claro! Tenemos el Air Zoom Pegasus 40 de Nike ideal para correr, disponible en talla 42 por $120.0 y nos quedan 5 unidades en stock.\n\n¿Te gustaría saber más sobre ellos o buscar otras opciones?",
  "timestamp": "2026-04-27T06:09:34.160239"
}
```

---

## Tests

```bash
pytest
pytest --tb=short -v   # con más detalle
```

24 tests en total: 19 para las entidades del dominio y 5 para los servicios usando mocks.

---

## Estructura completa

```
e-commerce-chat-ai/
├── src/
│   ├── config.py                      # Carga variables de entorno
│   ├── domain/
│   │   ├── entities.py                # Product, ChatMessage, ChatContext
│   │   ├── repositories.py            # Interfaces IProductRepository, IChatRepository
│   │   └── exceptions.py              # ProductNotFoundError, ChatServiceError
│   ├── application/
│   │   ├── dtos.py                    # DTOs con validación Pydantic
│   │   ├── product_service.py         # Casos de uso de productos
│   │   └── chat_service.py            # Caso de uso del chat con IA
│   └── infrastructure/
│       ├── api/main.py                # App FastAPI con todos los endpoints
│       ├── db/                        # SQLAlchemy: setup, modelos ORM, datos iniciales
│       ├── repositories/              # Implementaciones SQL de las interfaces
│       └── llm_providers/             # Integración con Google Gemini
├── tests/
│   ├── test_entities.py               # Tests del dominio
│   └── test_services.py               # Tests de servicios con mocks
├── evidencias/                        # Screenshots requeridos
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

"""
Punto de entrada de la aplicación FastAPI.

Define todos los endpoints HTTP y conecta la capa de infraestructura
con los servicios de aplicación. Cada endpoint crea los repositorios
y servicios que necesita usando la sesión de BD inyectada por FastAPI.
"""

from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)
from src.domain.exceptions import ProductNotFoundError, ChatServiceError

app = FastAPI(
    title="E-commerce Chat AI",
    description="API REST de e-commerce de zapatos con chat inteligente usando Google Gemini.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    """
    Se ejecuta una sola vez al iniciar la aplicación.

    Crea las tablas en SQLite si no existen y carga los datos iniciales.
    """
    init_db()


@app.get("/")
def root():
    """
    Endpoint raíz con información básica de la API.

    Returns:
        dict: Nombre, versión y lista de endpoints disponibles.
    """
    return {
        "nombre": "E-commerce Chat AI",
        "version": "1.0.0",
        "endpoints": [
            "GET  /products",
            "GET  /products/{id}",
            "POST /chat",
            "GET  /chat/history/{session_id}",
            "DELETE /chat/history/{session_id}",
            "GET  /health",
        ],
    }


@app.get("/health")
def health_check():
    """
    Health check para verificar que la API está activa.

    Returns:
        dict: Estado del servicio y timestamp actual.
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/products", response_model=List[ProductDTO])
def get_products(db: Session = Depends(get_db)):
    """
    Retorna el catálogo completo de productos.

    Args:
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        List[ProductDTO]: Todos los productos registrados.

    Example:
        GET /products
        Response: [{"id": 1, "name": "Air Zoom Pegasus 40", ...}, ...]
    """
    service = ProductService(SQLProductRepository(db))
    return service.get_all_products()


@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Busca un producto específico por su ID.

    Args:
        product_id (int): ID del producto en la URL.
        db (Session): Sesión de base de datos.

    Returns:
        ProductDTO: El producto encontrado.

    Raises:
        HTTPException: 404 si el producto no existe.
    """
    service = ProductService(SQLProductRepository(db))
    try:
        return service.get_product_by_id(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/chat", response_model=ChatMessageResponseDTO)
async def chat(request: ChatMessageRequestDTO, db: Session = Depends(get_db)):
    """
    Procesa un mensaje del usuario y retorna la respuesta generada por Gemini AI.

    Crea todos los servicios necesarios, delega al ChatService y maneja
    errores convirtiéndolos en respuestas HTTP apropiadas.

    Args:
        request (ChatMessageRequestDTO): Body con session_id y message.
        db (Session): Sesión de base de datos.

    Returns:
        ChatMessageResponseDTO: Respuesta del asistente junto al mensaje original.

    Raises:
        HTTPException: 500 si hay un error al llamar a la IA o al persistir.

    Example:
        POST /chat
        Body: {"session_id": "user123", "message": "Busco zapatos para correr"}
        Response: {"session_id": "user123", "user_message": "...", "assistant_message": "..."}
    """
    service = ChatService(
        product_repo=SQLProductRepository(db),
        chat_repo=SQLChatRepository(db),
        ai_service=GeminiService(),
    )
    try:
        return await service.process_message(request)
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO])
def get_chat_history(
    session_id: str, limit: int = 10, db: Session = Depends(get_db)
):
    """
    Retorna el historial de mensajes de una sesión.

    Args:
        session_id (str): ID de la sesión en la URL.
        limit (int): Máximo de mensajes a retornar. Default: 10.
        db (Session): Sesión de base de datos.

    Returns:
        List[ChatHistoryDTO]: Mensajes de la sesión en orden cronológico.
    """
    service = ChatService(
        product_repo=SQLProductRepository(db),
        chat_repo=SQLChatRepository(db),
        ai_service=None,
    )
    return service.get_session_history(session_id, limit=limit)


@app.delete("/chat/history/{session_id}")
def delete_chat_history(session_id: str, db: Session = Depends(get_db)):
    """
    Elimina el historial completo de una sesión de chat.

    Args:
        session_id (str): ID de la sesión a limpiar.
        db (Session): Sesión de base de datos.

    Returns:
        dict: Cantidad de mensajes eliminados.
    """
    service = ChatService(
        product_repo=SQLProductRepository(db),
        chat_repo=SQLChatRepository(db),
        ai_service=None,
    )
    deleted = service.clear_session_history(session_id)
    return {"session_id": session_id, "mensajes_eliminados": deleted}

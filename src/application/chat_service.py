"""
Caso de uso principal del sistema: procesar un mensaje de chat con IA.

Coordina tres cosas: obtener el catálogo de productos, recuperar el historial
de la conversación, y llamar a Gemini con toda esa información para que la
respuesta sea coherente con lo que el usuario ya preguntó antes.
"""

from datetime import datetime
from typing import List, Optional

from src.domain.entities import ChatMessage, ChatContext
from src.domain.repositories import IProductRepository, IChatRepository
from src.domain.exceptions import ChatServiceError
from src.application.dtos import (
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)


class ChatService:
    """
    Orquesta el flujo completo de una interacción de chat.

    Recibe los repositorios y el servicio de IA como parámetros (no los crea
    internamente) para poder pasar mocks en los tests sin tocar la BD.
    """

    def __init__(
        self,
        product_repo: IProductRepository,
        chat_repo: IChatRepository,
        ai_service,
    ) -> None:
        """
        Inicializa el servicio con sus tres colaboradores.

        Args:
            product_repo (IProductRepository): Fuente de datos de productos.
            chat_repo (IChatRepository): Fuente de datos del historial de chat.
            ai_service: Servicio que encapsula la llamada a Gemini API.
        """
        self._product_repo = product_repo
        self._chat_repo = chat_repo
        self._ai_service = ai_service

    async def process_message(
        self, request: ChatMessageRequestDTO
    ) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje y retorna la respuesta de la IA.

        Llama a Gemini ANTES de persistir — si falla la IA, no guardamos
        un mensaje del usuario sin respuesta en la BD.

        Raises:
            ChatServiceError: Si falla la llamada a Gemini o la persistencia.
        """
        try:
            products = self._product_repo.get_all()

            recent_msgs = self._chat_repo.get_recent_messages(
                session_id=request.session_id, count=6
            )
            context = ChatContext(messages=recent_msgs)

            assistant_response = await self._ai_service.generate_response(
                user_message=request.message,
                products=products,
                context=context,
            )

            now = datetime.utcnow()

            user_msg = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=now,
            )
            self._chat_repo.save_message(user_msg)

            assistant_msg = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=assistant_response,
                timestamp=now,
            )
            self._chat_repo.save_message(assistant_msg)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=assistant_response,
                timestamp=now,
            )

        except Exception as exc:
            raise ChatServiceError(
                f"Error al procesar el mensaje: {str(exc)}"
            ) from exc

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatHistoryDTO]:
        """
        Recupera el historial de mensajes de una sesión.

        Args:
            session_id (str): Identificador de la sesión a consultar.
            limit (Optional[int]): Si se proporciona, retorna solo los
                últimos N mensajes. Si es None, retorna todo el historial.

        Returns:
            List[ChatHistoryDTO]: Mensajes en orden cronológico.
        """
        messages = self._chat_repo.get_session_history(
            session_id=session_id, limit=limit
        )
        return [self._message_to_dto(m) for m in messages]

    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de una sesión de chat.

        Útil cuando el usuario quiere empezar una conversación desde cero.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados.
        """
        return self._chat_repo.delete_session_history(session_id)

    def _message_to_dto(self, message: ChatMessage) -> ChatHistoryDTO:
        """
        Convierte una entidad ChatMessage a su DTO de historial.

        Args:
            message (ChatMessage): Entidad del dominio.

        Returns:
            ChatHistoryDTO: DTO listo para serializar.
        """
        return ChatHistoryDTO(
            id=message.id,
            role=message.role,
            message=message.message,
            timestamp=message.timestamp,
        )

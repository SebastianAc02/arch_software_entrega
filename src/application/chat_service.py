"""
Servicio de aplicación para el chat inteligente con IA.

Este es el caso de uso más complejo del sistema: orquesta tres colaboradores
(repositorio de productos, repositorio de chat y servicio de IA) para procesar
un mensaje y generar una respuesta contextualizada.

La IA no se llama directamente desde el endpoint HTTP porque la lógica de
"qué productos incluir en el contexto" y "cómo construir el historial"
es decisión de la aplicación, no de la infraestructura.
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
    Servicio de aplicación que gestiona el flujo completo del chat con IA.

    Implementa el patrón de Inyección de Dependencias: recibe los tres
    colaboradores que necesita en el constructor, sin crearlos internamente.
    Esto facilita el testing (se pasan mocks) y el desacoplamiento entre capas.

    Attributes:
        _product_repo (IProductRepository): Repositorio de productos para
            obtener el catálogo que la IA usará como contexto.
        _chat_repo (IChatRepository): Repositorio de chat para guardar y
            recuperar el historial conversacional.
        _ai_service: Servicio de IA (GeminiService) para generar respuestas.
            Se tipifica como Any para evitar dependencia circular con infraestructura.
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
        Procesa un mensaje del usuario y retorna la respuesta del asistente de IA.

        Flujo completo del caso de uso:
        1. Obtiene todos los productos disponibles (contexto para la IA).
        2. Recupera los últimos 6 mensajes de la sesión (memoria conversacional).
        3. Construye un ChatContext con ese historial.
        4. Llama a la IA con: mensaje actual + productos + contexto previo.
        5. Persiste el mensaje del usuario en la base de datos.
        6. Persiste la respuesta del asistente en la base de datos.
        7. Retorna un DTO con ambos mensajes y el timestamp.

        El orden importa: primero se llama a la IA (puede fallar), luego
        se persiste. Así no guardamos un mensaje sin respuesta en caso de error.

        Args:
            request (ChatMessageRequestDTO): Datos del mensaje entrante.

        Returns:
            ChatMessageResponseDTO: Intercambio completo (usuario + asistente).

        Raises:
            ChatServiceError: Si ocurre algún error al llamar a la IA o al
                persistir los mensajes.
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

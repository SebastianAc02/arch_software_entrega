"""
Implementación concreta del repositorio de chat con SQLAlchemy.

Guarda y recupera mensajes del historial de conversación.
El orden cronológico es importante: la IA necesita los mensajes
de más antiguo a más reciente para entender el hilo de la conversación.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """
    Repositorio de mensajes de chat con persistencia en SQLite.

    Attributes:
        db (Session): Sesión de SQLAlchemy inyectada desde FastAPI.
    """

    def __init__(self, db: Session) -> None:
        """
        Args:
            db (Session): Sesión de base de datos inyectada.
        """
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Persiste un mensaje de chat y retorna la versión con ID asignado.

        Args:
            message (ChatMessage): Mensaje a guardar.

        Returns:
            ChatMessage: El mismo mensaje con el ID generado por la BD.
        """
        model = ChatMemoryModel(
            session_id=message.session_id,
            role=message.role,
            message=message.message,
            timestamp=message.timestamp,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Obtiene el historial completo o parcial de una sesión.

        Args:
            session_id (str): ID de la sesión a consultar.
            limit (Optional[int]): Si se da, retorna solo los últimos N mensajes.

        Returns:
            List[ChatMessage]: Mensajes ordenados de más antiguo a más reciente.
        """
        query = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.asc())
        )
        if limit:
            # Para obtener los últimos N en orden asc, primero ordeno desc, tomo N, y revierto
            query = (
                self.db.query(ChatMemoryModel)
                .filter(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.timestamp.desc())
                .limit(limit)
            )
            models = list(reversed(query.all()))
        else:
            models = query.all()

        return [self._to_entity(m) for m in models]

    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesión.

        Args:
            session_id (str): ID de la sesión a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        deleted = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return deleted

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Retorna los últimos N mensajes de una sesión en orden cronológico.

        Se usa para construir el contexto que se envía a Gemini. Ordenar
        desc y luego invertir garantiza el orden correcto sin subconsultas.

        Args:
            session_id (str): ID de la sesión.
            count (int): Cuántos mensajes recientes recuperar.

        Returns:
            List[ChatMessage]: Últimos N mensajes, de más antiguo a más reciente.
        """
        models = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
            .all()
        )
        return [self._to_entity(m) for m in reversed(models)]

    def _to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """
        Convierte un modelo ORM a entidad de dominio.

        Args:
            model (ChatMemoryModel): Fila de la tabla chat_memory.

        Returns:
            ChatMessage: Entidad del dominio.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

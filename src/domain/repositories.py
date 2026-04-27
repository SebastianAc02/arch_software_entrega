"""
Interfaces de repositorios: definen qué operaciones existen sobre los datos.

La implementación concreta (SQL, MongoDB, lo que sea) va en infrastructure/.
Esto permite testear los servicios pasando mocks sin necesitar base de datos real.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage


class IProductRepository(ABC):
    """Interface para acceso al catálogo de productos."""

    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos del catálogo.

        Returns:
            List[Product]: Lista de todos los productos registrados.
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su identificador único.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            Optional[Product]: El producto si existe, None en caso contrario.
        """
        pass

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Filtra productos por marca.

        Args:
            brand (str): Nombre de la marca (ej: 'Nike', 'Adidas').

        Returns:
            List[Product]: Lista de productos de esa marca.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Filtra productos por categoría de uso.

        Args:
            category (str): Categoría (ej: 'Running', 'Casual', 'Formal').

        Returns:
            List[Product]: Lista de productos de esa categoría.
        """
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Crea o actualiza un producto según tenga id=None o no.

        Returns:
            Product: El producto guardado, con ID asignado si era nuevo.
        """
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por su ID.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si se eliminó exitosamente, False si no existía.
        """
        pass


class IChatRepository(ABC):
    """Interface para guardar y recuperar el historial de conversaciones."""

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Persiste un mensaje de chat en el historial.

        Args:
            message (ChatMessage): Mensaje a guardar.

        Returns:
            ChatMessage: El mensaje guardado, con ID asignado por la base de datos.
        """
        pass

    @abstractmethod
    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Obtiene el historial completo (o parcial) de una sesión.

        Args:
            session_id (str): Identificador de la sesión del usuario.
            limit (Optional[int]): Si se especifica, retorna solo los últimos N mensajes.

        Returns:
            List[ChatMessage]: Mensajes en orden cronológico (más antiguo primero).
        """
        pass

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de una sesión de chat.

        Útil para limpiar conversaciones antiguas o cuando el usuario
        quiere empezar una conversación nueva.

        Args:
            session_id (str): Identificador de la sesión a eliminar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Retorna los últimos N mensajes de una sesión en orden cronológico.

        Es el método que usa ChatService para construir el contexto antes de llamar a la IA.
        """
        pass

"""
Interfaces (contratos) de los repositorios del dominio.

Define QUÉ operaciones existen sobre los datos, sin especificar CÓMO se implementan.
Esto es el patrón Repository: el dominio declara lo que necesita y la infraestructura
lo provee. Si mañana cambias SQLite por MongoDB, solo cambias la implementación
en la capa de infraestructura — el dominio y la aplicación no se tocan.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage


class IProductRepository(ABC):
    """
    Contrato abstracto para el acceso a datos de productos.

    Define las operaciones CRUD y de consulta disponibles sobre el catálogo
    de productos. La implementación concreta (SQLProductRepository) vive en
    la capa de infraestructura.

    Al heredar de ABC y decorar con @abstractmethod, Python garantiza que
    ninguna subclase pueda instanciarse sin implementar todos los métodos.
    """

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
        Persiste un producto (crea o actualiza).

        Si el producto tiene id=None, lo crea y asigna un nuevo ID.
        Si ya tiene ID, actualiza el registro existente.

        Args:
            product (Product): Producto a guardar.

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
    """
    Contrato abstracto para el acceso al historial de conversaciones.

    Gestiona la persistencia de mensajes de chat, permitiendo recuperar
    el contexto conversacional necesario para que la IA genere respuestas coherentes.
    """

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
        Obtiene los últimos N mensajes de una sesión, en orden cronológico.

        Es el método principal para construir el contexto conversacional
        que se envía a la IA. Limitar a los últimos N mensajes evita
        prompts excesivamente largos y costosos.

        Args:
            session_id (str): Identificador de la sesión.
            count (int): Número de mensajes recientes a recuperar.

        Returns:
            List[ChatMessage]: Últimos N mensajes, ordenados de más antiguo a más reciente.
        """
        pass

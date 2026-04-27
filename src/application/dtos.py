"""
Data Transfer Objects (DTOs) de la capa de aplicación.

Los DTOs son objetos cuyo único propósito es transportar datos entre capas.
Pydantic los valida automáticamente al instanciarlos: si un campo no cumple
las reglas, lanza ValidationError antes de que el dato entre al sistema.

Diferencia clave con las Entidades del Dominio:
- Las Entidades contienen lógica de negocio (reduce_stock, is_available).
- Los DTOs solo validan estructura y tipos; no tienen comportamiento.
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ProductDTO(BaseModel):
    """
    DTO para representar un producto en la API.

    Usado tanto para retornar productos al cliente como para recibir
    datos de creación/actualización. Pydantic v2 infiere el tipo y
    valida automáticamente al construir la instancia.

    Attributes:
        id (Optional[int]): None cuando es un producto nuevo (sin ID en BD).
        name (str): Nombre del zapato.
        brand (str): Marca (Nike, Adidas, Puma...).
        category (str): Categoría de uso (Running, Casual, Formal).
        size (str): Talla del zapato.
        color (str): Color.
        price (float): Precio en dólares. Debe ser mayor a 0.
        stock (int): Unidades disponibles. No puede ser negativo.
        description (str): Descripción del producto.
    """

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        """
        Valida que el precio sea mayor a cero.

        Args:
            v (float): Valor del campo price recibido.

        Raises:
            ValueError: Si el precio es menor o igual a cero.

        Returns:
            float: El precio validado.
        """
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return v

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, v: int) -> int:
        """
        Valida que el stock no sea negativo.

        Args:
            v (int): Valor del campo stock recibido.

        Raises:
            ValueError: Si el stock es negativo.

        Returns:
            int: El stock validado.
        """
        if v < 0:
            raise ValueError("El stock no puede ser negativo.")
        return v

    model_config = {"from_attributes": True}


class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir un mensaje de chat del cliente.

    El cliente envía este objeto en el body del POST /chat.
    Pydantic rechaza automáticamente peticiones con campos vacíos o faltantes.

    Attributes:
        session_id (str): Identificador único de la sesión del usuario.
            Permite mantener conversaciones separadas entre distintos usuarios.
        message (str): Texto del mensaje enviado por el usuario.
    """

    session_id: str
    message: str

    @field_validator("session_id")
    @classmethod
    def session_id_not_empty(cls, v: str) -> str:
        """
        Valida que el session_id no esté vacío ni solo con espacios.

        Raises:
            ValueError: Si session_id está vacío.
        """
        if not v or not v.strip():
            raise ValueError("El session_id no puede estar vacío.")
        return v.strip()

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """
        Valida que el mensaje no esté vacío ni solo con espacios.

        Raises:
            ValueError: Si el mensaje está vacío.
        """
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        return v.strip()


class ChatMessageResponseDTO(BaseModel):
    """
    DTO para retornar la respuesta del chat al cliente.

    Contiene tanto el mensaje original del usuario como la respuesta
    generada por la IA, facilitando que el cliente actualice su UI.

    Attributes:
        session_id (str): Identificador de la sesión.
        user_message (str): Mensaje original que envió el usuario.
        assistant_message (str): Respuesta generada por Gemini AI.
        timestamp (datetime): Momento en que se procesó el intercambio.
    """

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """
    DTO para representar un mensaje individual dentro del historial.

    Usado en el endpoint GET /chat/history/{session_id} para listar
    todos los mensajes de una sesión de forma paginada.

    Attributes:
        id (int): Identificador único del mensaje en la base de datos.
        role (str): Quién envió el mensaje ('user' o 'assistant').
        message (str): Contenido del mensaje.
        timestamp (datetime): Momento en que se creó el mensaje.
    """

    id: int
    role: str
    message: str
    timestamp: datetime

    model_config = {"from_attributes": True}

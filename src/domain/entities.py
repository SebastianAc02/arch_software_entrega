"""
Entidades del dominio: Product, ChatMessage y ChatContext.

Sin dependencias externas — ni FastAPI, ni SQLAlchemy, ni nada. Si esta capa
necesitara importar algo de infraestructura, algo estaría mal en el diseño.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """
    Representa un zapato en el inventario.

    Attributes:
        id: None si todavía no se guardó en la BD.
        name: No puede estar vacío.
        price: Debe ser mayor a 0.
        stock: No puede ser negativo.
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self) -> None:
        """
        Valida los datos del producto al crearlo.

        Raises:
            ValueError: Si el nombre está vacío, el precio es <= 0, o el stock es negativo.
        """
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if self.price <= 0:
            raise ValueError(f"El precio debe ser mayor a 0. Se recibió: {self.price}")
        if self.stock < 0:
            raise ValueError(f"El stock no puede ser negativo. Se recibió: {self.stock}")

    def is_available(self) -> bool:
        """Retorna True si hay unidades disponibles."""
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Descuenta del inventario al realizar una venta.

        Args:
            quantity (int): Debe ser positivo y no mayor al stock actual.

        Raises:
            ValueError: Si la cantidad no es válida o no hay suficiente stock.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva.")
        if quantity > self.stock:
            raise ValueError(
                f"Stock insuficiente. Disponible: {self.stock}, solicitado: {quantity}."
            )
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        Agrega unidades al inventario.

        Raises:
            ValueError: Si quantity <= 0.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva.")
        self.stock += quantity


@dataclass
class ChatMessage:
    """
    Un mensaje dentro de una conversación de chat.

    Attributes:
        session_id: Agrupa todos los mensajes de un mismo usuario/conversación.
        role: Solo acepta 'user' o 'assistant'.
    """

    id: Optional[int]
    session_id: str
    role: str
    message: str
    timestamp: datetime

    def __post_init__(self) -> None:
        """
        Raises:
            ValueError: Si role no es válido, o si message/session_id están vacíos.
        """
        valid_roles = {"user", "assistant"}
        if self.role not in valid_roles:
            raise ValueError(
                f"El role debe ser 'user' o 'assistant'. Se recibió: '{self.role}'"
            )
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío.")

    def is_from_user(self) -> bool:
        """
        Verifica si el mensaje fue enviado por el usuario humano.

        Returns:
            bool: True si role == 'user'.
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """
        Verifica si el mensaje fue generado por el asistente de IA.

        Returns:
            bool: True si role == 'assistant'.
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """
    Mantiene el historial reciente de una conversación para pasárselo a la IA.

    Limitar a max_messages evita que el prompt crezca indefinidamente con cada
    mensaje nuevo — con 6 mensajes hay contexto suficiente para ser coherente.
    """

    messages: list
    max_messages: int = 6

    def get_recent_messages(self) -> list:
        """Retorna los últimos max_messages mensajes en orden cronológico."""
        return self.messages[-self.max_messages:]

    def format_for_prompt(self) -> str:
        """
        Convierte el historial a texto plano para incluir en el prompt de Gemini.

        Formato: "Usuario: ...\nAsistente: ..."
        Retorna string vacío si no hay mensajes.
        """
        recent = self.get_recent_messages()
        if not recent:
            return ""

        role_labels = {"user": "Usuario", "assistant": "Asistente"}
        lines = []
        for msg in recent:
            label = role_labels.get(msg.role, msg.role.capitalize())
            lines.append(f"{label}: {msg.message}")
        return "\n".join(lines)

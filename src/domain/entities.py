"""
Entidades del dominio de negocio.

Este módulo contiene los objetos centrales del negocio: productos y mensajes de chat.
No depende de ningún framework, base de datos ni servicio externo.
Es la capa más interna de la Clean Architecture.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """
    Entidad que representa un zapato en el inventario del e-commerce.

    Encapsula las reglas de negocio sobre productos: validaciones de precio,
    stock y disponibilidad. Al ser un dataclass, los atributos se definen
    declarativamente y __post_init__ se ejecuta automáticamente al crear el objeto.

    Attributes:
        id (Optional[int]): Identificador único. None cuando el producto aún no
            ha sido persistido en la base de datos.
        name (str): Nombre del producto, no puede estar vacío.
        brand (str): Marca del zapato (Nike, Adidas, Puma, etc.).
        category (str): Categoría de uso (Running, Casual, Formal).
        size (str): Talla del zapato.
        color (str): Color del zapato.
        price (float): Precio en dólares. Debe ser mayor a 0.
        stock (int): Unidades disponibles. No puede ser negativo.
        description (str): Descripción detallada del producto.
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
        Valida las invariantes del producto al momento de creación.

        Se ejecuta automáticamente después de __init__ (comportamiento de dataclass).
        Implementa el principio "Fail Fast": si los datos son inválidos, falla
        inmediatamente en lugar de propagar el error a capas superiores.

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
        """
        Verifica si el producto tiene unidades disponibles para venta.

        Returns:
            bool: True si stock > 0, False en caso contrario.

        Example:
            >>> p = Product(id=1, name="Nike Air", brand="Nike", category="Running",
            ...             size="42", color="Negro", price=120.0, stock=5, description="...")
            >>> p.is_available()
            True
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock del producto al realizar una venta.

        Valida que la cantidad sea positiva y que haya suficiente inventario.
        Esta lógica vive en el dominio porque es una regla de negocio, no un
        detalle técnico de base de datos.

        Args:
            quantity (int): Cantidad a descontar del inventario. Debe ser positivo.

        Raises:
            ValueError: Si quantity <= 0 o si el stock disponible es insuficiente.

        Example:
            >>> p = Product(id=1, name="Nike Air", ..., stock=10, ...)
            >>> p.reduce_stock(3)
            >>> p.stock
            7
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
        Aumenta el stock del producto al recibir nuevo inventario.

        Args:
            quantity (int): Cantidad a agregar al inventario. Debe ser positiva.

        Raises:
            ValueError: Si quantity <= 0.

        Example:
            >>> p = Product(id=1, name="Nike Air", ..., stock=5, ...)
            >>> p.increase_stock(10)
            >>> p.stock
            15
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva.")
        self.stock += quantity


@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje individual en una conversación de chat.

    Cada mensaje pertenece a una sesión (usuario) y tiene un rol que indica
    quién lo envió: el usuario humano o el asistente de IA.

    Attributes:
        id (Optional[int]): Identificador único en base de datos. None si no fue persistido.
        session_id (str): Identificador de la sesión del usuario. Agrupa los mensajes
            de una misma conversación.
        role (str): Quién envió el mensaje. Solo acepta 'user' o 'assistant'.
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Momento exacto en que se creó el mensaje.
    """

    id: Optional[int]
    session_id: str
    role: str
    message: str
    timestamp: datetime

    def __post_init__(self) -> None:
        """
        Valida las invariantes del mensaje al momento de creación.

        Raises:
            ValueError: Si el role no es válido, el mensaje está vacío, o session_id está vacío.
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
    Value Object que encapsula el contexto conversacional para la IA.

    Mantiene los mensajes recientes de una sesión para que el modelo de IA
    pueda generar respuestas coherentes con el hilo de la conversación.
    Un Value Object (a diferencia de una Entidad) se define por su contenido,
    no por un identificador único.

    Attributes:
        messages (list[ChatMessage]): Lista completa de mensajes de la sesión.
        max_messages (int): Máximo de mensajes recientes a considerar. Default: 6.
            Limitar el contexto controla el tamaño del prompt enviado a la IA.
    """

    messages: list
    max_messages: int = 6

    def get_recent_messages(self) -> list:
        """
        Retorna los últimos N mensajes de la conversación.

        Usar slicing negativo [-N:] es idiomático en Python para obtener
        los últimos N elementos de una lista.

        Returns:
            list[ChatMessage]: Los últimos max_messages mensajes, en orden cronológico.
        """
        return self.messages[-self.max_messages:]

    def format_for_prompt(self) -> str:
        """
        Formatea el historial reciente como texto para incluir en el prompt de la IA.

        Convierte la lista de mensajes estructurados en un texto que el modelo
        puede leer y usar como contexto. El formato usa los roles en español
        para que el modelo responda coherentemente en español.

        Returns:
            str: Historial formateado. Ejemplo:
                "Usuario: Busco zapatos para correr\\nAsistente: Tengo varias opciones..."
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

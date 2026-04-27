"""
Modelos ORM de SQLAlchemy.

Estos modelos representan las tablas en SQLite. Son distintos a las entidades
del dominio: las entidades tienen lógica de negocio, los modelos solo mapean
columnas a Python. La conversión entre ambos la hacen los repositorios.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index
from src.infrastructure.db.database import Base


class ProductModel(Base):
    """
    Tabla 'products' en la base de datos.

    Guarda el catálogo de zapatos del e-commerce.

    Attributes:
        id (int): Clave primaria autoincremental.
        name (str): Nombre del producto.
        brand (str): Marca del zapato.
        category (str): Categoría de uso.
        size (str): Talla.
        color (str): Color.
        price (float): Precio en dólares.
        stock (int): Unidades disponibles.
        description (str): Descripción larga del producto.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100))
    category = Column(String(100))
    size = Column(String(20))
    color = Column(String(50))
    price = Column(Float)
    stock = Column(Integer)
    description = Column(Text)


class ChatMemoryModel(Base):
    """
    Tabla 'chat_memory' en la base de datos.

    Persiste cada mensaje del chat para que la IA pueda recordar
    conversaciones anteriores de cada usuario.

    Attributes:
        id (int): Clave primaria.
        session_id (str): Identificador de la sesión del usuario. Indexado
            porque lo consultamos frecuentemente para recuperar historial.
        role (str): 'user' o 'assistant'.
        message (str): Contenido del mensaje.
        timestamp (datetime): Cuándo se creó el mensaje.
    """

    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_chat_memory_session_id", "session_id"),
    )

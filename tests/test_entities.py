"""
Tests unitarios para las entidades del dominio.

Testeo las reglas de negocio directamente sobre las entidades,
sin base de datos ni servicios externos. Si estas pruebas fallan,
hay un bug en la lógica de negocio central.
"""

import pytest
from datetime import datetime

from src.domain.entities import Product, ChatMessage, ChatContext


class TestProduct:
    """Tests para la entidad Product."""

    def test_crear_producto_valido(self):
        """Un producto con datos correctos debe crearse sin errores."""
        p = Product(
            id=None,
            name="Stan Smith",
            brand="Adidas",
            category="Formal",
            size="41",
            color="Blanco",
            price=85.0,
            stock=9,
            description="El tenis más vendido de la historia.",
        )
        assert p.name == "Stan Smith"
        assert p.price == 85.0

    def test_precio_negativo_lanza_error(self):
        """No debería poder crear un producto con precio negativo."""
        with pytest.raises(ValueError, match="precio"):
            Product(
                id=None, name="Zapato", brand="X", category="Casual",
                size="40", color="Rojo", price=-10.0, stock=5,
                description="desc",
            )

    def test_precio_cero_lanza_error(self):
        """Precio igual a cero tampoco es válido."""
        with pytest.raises(ValueError):
            Product(
                id=None, name="Zapato", brand="X", category="Casual",
                size="40", color="Rojo", price=0, stock=5, description="desc",
            )

    def test_stock_negativo_lanza_error(self):
        """El stock no puede ser negativo."""
        with pytest.raises(ValueError, match="stock"):
            Product(
                id=None, name="Zapato", brand="X", category="Casual",
                size="40", color="Rojo", price=50.0, stock=-1,
                description="desc",
            )

    def test_nombre_vacio_lanza_error(self):
        """El nombre no puede estar vacío."""
        with pytest.raises(ValueError):
            Product(
                id=None, name="   ", brand="X", category="Casual",
                size="40", color="Rojo", price=50.0, stock=5, description="desc",
            )

    def test_is_available_con_stock(self, sample_product):
        """is_available debe retornar True cuando hay stock."""
        assert sample_product.is_available() is True

    def test_is_available_sin_stock(self, sample_product):
        """is_available debe retornar False cuando stock es 0."""
        sample_product.stock = 0
        assert sample_product.is_available() is False

    def test_reduce_stock(self, sample_product):
        """reduce_stock debe descontar correctamente."""
        stock_inicial = sample_product.stock
        sample_product.reduce_stock(2)
        assert sample_product.stock == stock_inicial - 2

    def test_reduce_stock_insuficiente(self, sample_product):
        """No se puede reducir más stock del disponible."""
        with pytest.raises(ValueError):
            sample_product.reduce_stock(100)

    def test_increase_stock(self, sample_product):
        """increase_stock debe sumar correctamente."""
        stock_inicial = sample_product.stock
        sample_product.increase_stock(3)
        assert sample_product.stock == stock_inicial + 3

    def test_increase_stock_negativo_lanza_error(self, sample_product):
        """No se puede aumentar el stock con cantidad negativa o cero."""
        with pytest.raises(ValueError):
            sample_product.increase_stock(0)


class TestChatMessage:
    """Tests para la entidad ChatMessage."""

    def test_crear_mensaje_valido(self):
        """Un mensaje con datos correctos debe crearse sin errores."""
        msg = ChatMessage(
            id=None,
            session_id="session-1",
            role="user",
            message="Hola",
            timestamp=datetime.utcnow(),
        )
        assert msg.role == "user"

    def test_role_invalido(self):
        """El role solo puede ser 'user' o 'assistant'."""
        with pytest.raises(ValueError, match="role"):
            ChatMessage(
                id=None, session_id="s1", role="admin",
                message="Hola", timestamp=datetime.utcnow(),
            )

    def test_mensaje_vacio_lanza_error(self):
        """El mensaje no puede estar vacío."""
        with pytest.raises(ValueError):
            ChatMessage(
                id=None, session_id="s1", role="user",
                message="", timestamp=datetime.utcnow(),
            )

    def test_is_from_user(self, sample_chat_message):
        """is_from_user debe retornar True para mensajes del usuario."""
        assert sample_chat_message.is_from_user() is True
        assert sample_chat_message.is_from_assistant() is False

    def test_is_from_assistant(self):
        """is_from_assistant debe retornar True para mensajes del asistente."""
        msg = ChatMessage(
            id=None, session_id="s1", role="assistant",
            message="Hola, ¿en qué te ayudo?", timestamp=datetime.utcnow(),
        )
        assert msg.is_from_assistant() is True
        assert msg.is_from_user() is False


class TestChatContext:
    """Tests para el value object ChatContext."""

    def _make_message(self, role: str, text: str) -> ChatMessage:
        return ChatMessage(
            id=None, session_id="s1", role=role,
            message=text, timestamp=datetime.utcnow(),
        )

    def test_get_recent_messages_limita_cantidad(self):
        """get_recent_messages debe retornar solo los últimos max_messages."""
        msgs = [self._make_message("user", f"msg {i}") for i in range(10)]
        ctx = ChatContext(messages=msgs, max_messages=6)
        recientes = ctx.get_recent_messages()
        assert len(recientes) == 6
        assert recientes[-1].message == "msg 9"

    def test_format_for_prompt_con_mensajes(self):
        """format_for_prompt debe formatear correctamente el historial."""
        msgs = [
            self._make_message("user", "Busco running"),
            self._make_message("assistant", "Tengo varias opciones"),
        ]
        ctx = ChatContext(messages=msgs)
        resultado = ctx.format_for_prompt()
        assert "Usuario: Busco running" in resultado
        assert "Asistente: Tengo varias opciones" in resultado

    def test_format_for_prompt_sin_mensajes(self):
        """Con lista vacía debe retornar string vacío."""
        ctx = ChatContext(messages=[])
        assert ctx.format_for_prompt() == ""

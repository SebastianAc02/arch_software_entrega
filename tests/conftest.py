"""
Fixtures compartidos para los tests.

pytest carga este archivo automáticamente antes de correr los tests.
Los fixtures acá disponibles en cualquier test sin necesidad de importar.
"""

import pytest
from datetime import datetime

from src.domain.entities import Product, ChatMessage, ChatContext


@pytest.fixture
def sample_product():
    """Retorna un producto válido para usar en tests."""
    return Product(
        id=1,
        name="Air Zoom Pegasus",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Zapatilla de running con amortiguación de aire.",
    )


@pytest.fixture
def sample_chat_message():
    """Retorna un mensaje de chat válido para usar en tests."""
    return ChatMessage(
        id=1,
        session_id="test-session",
        role="user",
        message="Hola, busco zapatos para correr",
        timestamp=datetime.utcnow(),
    )

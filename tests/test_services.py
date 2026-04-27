"""
Tests unitarios para los servicios de aplicación.

Uso mocks en lugar de repositorios reales para testear la lógica del servicio
sin necesitar base de datos. Si el test falla, el bug está en el servicio,
no en la base de datos ni en la IA.
"""

import pytest
from unittest.mock import MagicMock
from datetime import datetime

from src.domain.entities import Product, ChatMessage
from src.domain.exceptions import ProductNotFoundError
from src.application.product_service import ProductService
from src.application.dtos import ChatMessageRequestDTO


def make_product(product_id=1, stock=5):
    """Helper para crear productos de prueba rápidamente."""
    return Product(
        id=product_id,
        name=f"Producto {product_id}",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=100.0,
        stock=stock,
        description="Descripción de prueba.",
    )


class TestProductService:
    """Tests para ProductService."""

    def test_get_all_products(self):
        """get_all_products debe retornar todos los productos del repositorio."""
        mock_repo = MagicMock()
        mock_repo.get_all.return_value = [make_product(1), make_product(2)]

        service = ProductService(mock_repo)
        result = service.get_all_products()

        assert len(result) == 2
        mock_repo.get_all.assert_called_once()

    def test_get_product_by_id_existente(self):
        """Debe retornar el producto cuando existe."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = make_product(1)

        service = ProductService(mock_repo)
        result = service.get_product_by_id(1)

        assert result.id == 1
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_get_product_by_id_no_existente(self):
        """Debe lanzar ProductNotFoundError cuando el producto no existe."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        service = ProductService(mock_repo)

        with pytest.raises(ProductNotFoundError):
            service.get_product_by_id(999)

    def test_get_available_products_filtra_sin_stock(self):
        """Solo debe retornar productos con stock > 0."""
        mock_repo = MagicMock()
        mock_repo.get_all.return_value = [
            make_product(1, stock=5),
            make_product(2, stock=0),  # sin stock, no debe aparecer
            make_product(3, stock=3),
        ]

        service = ProductService(mock_repo)
        result = service.get_available_products()

        assert len(result) == 2
        assert all(p.stock > 0 for p in result)

    def test_delete_product(self):
        """delete_product debe llamar al repositorio y retornar el resultado."""
        mock_repo = MagicMock()
        mock_repo.delete.return_value = True

        service = ProductService(mock_repo)
        result = service.delete_product(1)

        assert result is True
        mock_repo.delete.assert_called_once_with(1)

"""
Servicio de aplicación para la gestión de productos.

Este módulo implementa los casos de uso relacionados con el catálogo de zapatos.
Orquesta el flujo entre la capa de dominio y la capa de infraestructura sin
conocer detalles técnicos como SQL o FastAPI.

Patrón aplicado: Service Layer — centraliza la lógica de aplicación para que
los endpoints HTTP sean delegadores delgados, no controladores gordos.
"""

from typing import List, Optional

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.domain.exceptions import ProductNotFoundError
from src.application.dtos import ProductDTO


class ProductService:
    """
    Servicio de aplicación que implementa los casos de uso de productos.

    Recibe el repositorio por inyección de dependencias (Dependency Injection):
    el servicio no sabe si detrás hay SQLite, PostgreSQL o un mock de tests.
    Esto permite testear la lógica sin necesidad de base de datos real.

    Attributes:
        _repo (IProductRepository): Repositorio de productos inyectado.
    """

    def __init__(self, repo: IProductRepository) -> None:
        """
        Inicializa el servicio con su repositorio.

        Args:
            repo (IProductRepository): Implementación concreta del repositorio.
                En producción será SQLProductRepository; en tests puede ser un mock.
        """
        self._repo = repo

    def get_all_products(self) -> List[ProductDTO]:
        """
        Retorna el catálogo completo de productos.

        Returns:
            List[ProductDTO]: Lista de todos los productos registrados.

        Example:
            >>> service = ProductService(repo)
            >>> products = service.get_all_products()
            >>> len(products) > 0
            True
        """
        products = self._repo.get_all()
        return [self._entity_to_dto(p) for p in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """
        Busca un producto específico por su identificador.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            ProductDTO: El producto encontrado.

        Raises:
            ProductNotFoundError: Si no existe ningún producto con ese ID.
        """
        product = self._repo.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return self._entity_to_dto(product)

    def get_available_products(self) -> List[ProductDTO]:
        """
        Retorna únicamente los productos con stock disponible.

        Filtra en memoria usando la lógica de negocio de la entidad (is_available),
        no con una query SQL directa. Así la regla "stock > 0" vive en el dominio.

        Returns:
            List[ProductDTO]: Productos con stock mayor a cero.
        """
        all_products = self._repo.get_all()
        return [self._entity_to_dto(p) for p in all_products if p.is_available()]

    def search_by_brand(self, brand: str) -> List[ProductDTO]:
        """
        Filtra productos por marca.

        Args:
            brand (str): Nombre de la marca a buscar (ej. 'Nike').

        Returns:
            List[ProductDTO]: Productos de esa marca.
        """
        products = self._repo.get_by_brand(brand)
        return [self._entity_to_dto(p) for p in products]

    def search_by_category(self, category: str) -> List[ProductDTO]:
        """
        Filtra productos por categoría de uso.

        Args:
            category (str): Categoría (ej. 'Running', 'Casual').

        Returns:
            List[ProductDTO]: Productos de esa categoría.
        """
        products = self._repo.get_by_category(category)
        return [self._entity_to_dto(p) for p in products]

    def create_product(self, dto: ProductDTO) -> ProductDTO:
        """
        Crea un nuevo producto en el catálogo.

        Convierte el DTO a Entidad para que las validaciones del dominio
        se ejecuten antes de persistir. Si los datos son inválidos,
        la entidad lanza ValueError antes de llegar a la base de datos.

        Args:
            dto (ProductDTO): Datos del nuevo producto.

        Returns:
            ProductDTO: El producto creado con su ID asignado.
        """
        entity = self._dto_to_entity(dto)
        saved = self._repo.save(entity)
        return self._entity_to_dto(saved)

    def update_product(self, product_id: int, dto: ProductDTO) -> ProductDTO:
        """
        Actualiza un producto existente.

        Verifica que el producto exista antes de actualizar para dar un
        error descriptivo (ProductNotFoundError) en lugar de un error genérico.

        Args:
            product_id (int): ID del producto a actualizar.
            dto (ProductDTO): Nuevos datos del producto.

        Returns:
            ProductDTO: El producto actualizado.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        existing = self._repo.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(product_id)

        entity = self._dto_to_entity(dto)
        entity.id = product_id
        saved = self._repo.save(entity)
        return self._entity_to_dto(saved)

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto del catálogo.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si se eliminó, False si no existía.
        """
        return self._repo.delete(product_id)

    def _entity_to_dto(self, product: Product) -> ProductDTO:
        """
        Convierte una Entidad de dominio a DTO de transferencia.

        La conversión es necesaria porque las entidades no deben exponerse
        directamente a capas externas (podrían tener métodos de negocio
        que no tienen sentido en una respuesta JSON).

        Args:
            product (Product): Entidad del dominio.

        Returns:
            ProductDTO: DTO listo para serializar como JSON.
        """
        return ProductDTO(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
        )

    def _dto_to_entity(self, dto: ProductDTO) -> Product:
        """
        Convierte un DTO recibido a Entidad de dominio.

        Al crear la entidad se ejecutan las validaciones de negocio (__post_init__),
        garantizando que los datos sean válidos antes de persistirlos.

        Args:
            dto (ProductDTO): DTO recibido desde la capa de infraestructura.

        Returns:
            Product: Entidad con validaciones de negocio aplicadas.
        """
        return Product(
            id=dto.id,
            name=dto.name,
            brand=dto.brand,
            category=dto.category,
            size=dto.size,
            color=dto.color,
            price=dto.price,
            stock=dto.stock,
            description=dto.description,
        )

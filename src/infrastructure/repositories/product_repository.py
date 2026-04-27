"""
Implementación concreta del repositorio de productos con SQLAlchemy.

Esta clase implementa la interfaz IProductRepository definida en el dominio.
Todo lo que tenga que ver con SQL vive acá: el dominio y la aplicación
no saben que estamos usando SQLite.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """
    Repositorio de productos con persistencia en SQLite via SQLAlchemy.

    Recibe la sesión de base de datos por inyección para que FastAPI
    pueda manejar su ciclo de vida (apertura/cierre) con Depends(get_db).

    Attributes:
        db (Session): Sesión activa de SQLAlchemy.
    """

    def __init__(self, db: Session) -> None:
        """
        Args:
            db (Session): Sesión de base de datos inyectada.
        """
        self.db = db

    def get_all(self) -> List[Product]:
        """
        Retorna todos los productos de la base de datos.

        Returns:
            List[Product]: Lista de entidades de dominio.
        """
        models = self.db.query(ProductModel).all()
        return [self._to_entity(m) for m in models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por ID.

        Args:
            product_id (int): ID a buscar.

        Returns:
            Optional[Product]: La entidad si existe, None si no.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Filtra productos por marca (case-insensitive).

        Args:
            brand (str): Nombre de la marca.

        Returns:
            List[Product]: Productos de esa marca.
        """
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.brand.ilike(f"%{brand}%"))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def get_by_category(self, category: str) -> List[Product]:
        """
        Filtra productos por categoría.

        Args:
            category (str): Categoría a buscar.

        Returns:
            List[Product]: Productos de esa categoría.
        """
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.category.ilike(f"%{category}%"))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto.

        Si tiene id=None lo crea; si tiene ID actualiza el registro existente.

        Args:
            product (Product): Entidad a persistir.

        Returns:
            Product: Entidad con ID asignado.
        """
        if product.id is None:
            model = self._to_model(product)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        else:
            model = self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
            if model:
                model.name = product.name
                model.brand = product.brand
                model.category = product.category
                model.size = product.size
                model.color = product.color
                model.price = product.price
                model.stock = product.stock
                model.description = product.description
                self.db.commit()
                self.db.refresh(model)
            return self._to_entity(model)

    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por ID.

        Args:
            product_id (int): ID del producto.

        Returns:
            bool: True si se eliminó, False si no existía.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    def _to_entity(self, model: ProductModel) -> Product:
        """
        Convierte un modelo ORM a entidad de dominio.

        Args:
            model (ProductModel): Fila de la base de datos.

        Returns:
            Product: Entidad de dominio con validaciones.
        """
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _to_model(self, product: Product) -> ProductModel:
        """
        Convierte una entidad de dominio a modelo ORM.

        Args:
            product (Product): Entidad del dominio.

        Returns:
            ProductModel: Objeto listo para persistir con SQLAlchemy.
        """
        return ProductModel(
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
        )

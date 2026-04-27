"""
Carga de datos iniciales al arrancar la aplicación.

Si la tabla de productos está vacía, inserto un catálogo de ejemplo con 10 zapatos
de distintas marcas y categorías. Esto permite probar el chat sin tener que
cargar datos manualmente.
"""

from sqlalchemy.orm import Session
from src.infrastructure.db.models import ProductModel


def load_initial_data(db: Session) -> None:
    """
    Inserta los productos de ejemplo si la base de datos está vacía.

    Args:
        db (Session): Sesión de SQLAlchemy abierta por el llamador.

    Returns:
        None
    """
    if db.query(ProductModel).count() > 0:
        return

    products = [
        ProductModel(
            name="Air Zoom Pegasus 40",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=5,
            description="Zapatilla de running con amortiguación de aire reactiva, ideal para distancias largas.",
        ),
        ProductModel(
            name="Ultraboost 23",
            brand="Adidas",
            category="Running",
            size="41",
            color="Blanco",
            price=150.0,
            stock=3,
            description="Tecnología Boost para máxima energía de retorno en cada zancada.",
        ),
        ProductModel(
            name="Suede Classic XXI",
            brand="Puma",
            category="Casual",
            size="40",
            color="Azul",
            price=80.0,
            stock=10,
            description="Clásico urbano con parte superior de ante, perfecto para el día a día.",
        ),
        ProductModel(
            name="Chuck Taylor All Star",
            brand="Converse",
            category="Casual",
            size="43",
            color="Rojo",
            price=65.0,
            stock=8,
            description="El ícono cultural que nunca pasa de moda, disponible en lona resistente.",
        ),
        ProductModel(
            name="Old Skool",
            brand="Vans",
            category="Casual",
            size="41",
            color="Negro/Blanco",
            price=75.0,
            stock=6,
            description="Silueta skate clásica con la icónica franja lateral Jazz Stripe.",
        ),
        ProductModel(
            name="Gel-Kayano 30",
            brand="Asics",
            category="Running",
            size="44",
            color="Gris",
            price=160.0,
            stock=4,
            description="Estabilidad y soporte superior para corredores de pronación.",
        ),
        ProductModel(
            name="574 Core",
            brand="New Balance",
            category="Casual",
            size="42",
            color="Verde",
            price=90.0,
            stock=7,
            description="Diseño retro con suela ENCAP para comodidad todo el día.",
        ),
        ProductModel(
            name="RS-X3",
            brand="Puma",
            category="Running",
            size="43",
            color="Blanco/Azul",
            price=100.0,
            stock=5,
            description="Estética chunky inspirada en los años 80 con tecnología Running System.",
        ),
        ProductModel(
            name="Stan Smith",
            brand="Adidas",
            category="Formal",
            size="40",
            color="Blanco",
            price=85.0,
            stock=9,
            description="El tenis más vendido de la historia, minimalista y versátil.",
        ),
        ProductModel(
            name="Air Force 1 '07",
            brand="Nike",
            category="Formal",
            size="41",
            color="Blanco",
            price=110.0,
            stock=2,
            description="Icónico diseño de 1982 con suela de aire visible y cuero premium.",
        ),
    ]

    db.add_all(products)
    db.commit()

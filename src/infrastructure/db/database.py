"""
Configuración de la base de datos con SQLAlchemy.

Acá defino el motor de conexión a SQLite, la sesión que usan los repositorios
y la función que inicializa las tablas al arrancar la app.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from src.config import settings


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # necesario para SQLite con FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base que heredan todos los modelos ORM del proyecto."""
    pass


def get_db():
    """
    Dependency de FastAPI que entrega una sesión de base de datos por request.

    Uso del patrón yield: garantiza que la sesión se cierra aunque ocurra
    una excepción en el endpoint. FastAPI llama esto automáticamente con Depends().

    Yields:
        Session: Sesión activa de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Crea todas las tablas definidas en los modelos ORM si no existen.

    Se llama una sola vez al iniciar la aplicación (evento startup de FastAPI).
    El import de models acá es intencional: necesito que SQLAlchemy haya visto
    los modelos antes de llamar create_all().

    Returns:
        None
    """
    from src.infrastructure.db import models  # noqa: F401
    from src.infrastructure.db.init_data import load_initial_data

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        load_initial_data(db)
    finally:
        db.close()

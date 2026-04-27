"""
Configuración global de la aplicación.

Lee variables de entorno desde el archivo .env mediante python-dotenv.
Centralizar la configuración en un único módulo evita que la lógica de
negocio conozca de dónde vienen los valores (archivo, variable de entorno, etc.).
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Contenedor de configuración global de la aplicación.

    Attributes:
        gemini_api_key (str): API key para autenticarse con Google Gemini.
        database_url (str): URL de conexión a la base de datos SQLite.
        environment (str): Entorno de ejecución ('development', 'production').
    """

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./data/ecommerce_chat.db"
    )
    environment: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()

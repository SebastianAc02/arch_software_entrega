"""
Servicio de integración con Google Gemini AI.

Encapsula todo lo relacionado con la API de Gemini para que el resto
del sistema no sepa qué modelo de IA se está usando. Si mañana
cambiamos a OpenAI o a un modelo local, solo tocamos este archivo.
"""

import google.generativeai as genai

from src.config import settings
from src.domain.entities import ChatContext


class GeminiService:
    """
    Cliente del servicio de IA de Google Gemini.

    Construye el prompt completo (sistema + productos + historial + mensaje)
    y llama a la API de Gemini para obtener la respuesta del asistente.

    Attributes:
        _model: Instancia del modelo Gemini configurado para generar texto.
    """

    def __init__(self) -> None:
        """
        Configura el cliente de Gemini con la API key del entorno.

        Raises:
            ValueError: Si GEMINI_API_KEY no está configurada.
        """
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY no configurada. Agrégala al archivo .env"
            )
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel("gemini-2.5-flash")

    async def generate_response(
        self,
        user_message: str,
        products: list,
        context: ChatContext,
    ) -> str:
        """
        Genera una respuesta de la IA dado un mensaje, el catálogo y el historial.

        El prompt tiene 4 partes:
        1. Instrucciones del sistema (quién es el asistente).
        2. Lista de productos disponibles en el inventario.
        3. Historial reciente de la conversación.
        4. El mensaje actual del usuario.

        Args:
            user_message (str): Mensaje que acaba de enviar el usuario.
            products (list): Lista de entidades Product del catálogo completo.
            context (ChatContext): Historial reciente de la conversación.

        Returns:
            str: Texto de respuesta generado por Gemini.

        Raises:
            Exception: Si la llamada a la API de Gemini falla.
        """
        products_text = self._format_products(products)
        history_text = context.format_for_prompt()

        prompt = f"""Eres un asistente de ventas de una tienda de zapatos online. \
Tu objetivo es ayudar a los clientes a encontrar el zapato ideal según sus necesidades.

PRODUCTOS DISPONIBLES EN INVENTARIO:
{products_text}

INSTRUCCIONES:
- Sé amable y directo, sin rodeos innecesarios.
- Usa el historial de la conversación para dar respuestas coherentes.
- Recomienda productos concretos mencionando nombre, precio, talla y stock.
- Si el cliente pregunta algo que no tiene que ver con zapatos, redirige amablemente.
- Responde siempre en español.

HISTORIAL DE LA CONVERSACIÓN:
{history_text if history_text else "Esta es la primera interacción."}

Usuario: {user_message}
Asistente:"""

        response = self._model.generate_content(prompt)
        return response.text.strip()

    def _format_products(self, products: list) -> str:
        """
        Convierte la lista de productos a texto plano para incluir en el prompt.

        Formato elegido: una línea por producto con los datos más relevantes
        para que la IA pueda referenciarlos fácilmente.

        Args:
            products (list): Lista de entidades Product.

        Returns:
            str: Texto formateado con un producto por línea.
        """
        if not products:
            return "No hay productos disponibles en este momento."

        lines = []
        for p in products:
            disponibilidad = f"{p.stock} unidades" if p.stock > 0 else "SIN STOCK"
            lines.append(
                f"- {p.name} | {p.brand} | {p.category} | Talla {p.size} | "
                f"${p.price} | {disponibilidad}"
            )
        return "\n".join(lines)

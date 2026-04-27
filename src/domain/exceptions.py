"""
Excepciones del dominio de negocio.

Representan errores de lógica de negocio, no errores técnicos.
Al tener excepciones propias del dominio, el código que las captura
sabe exactamente qué salió mal en términos del negocio, no en términos
de la base de datos o la red.
"""


class ProductNotFoundError(Exception):
    """
    Se lanza cuando se busca un producto que no existe en el catálogo.

    Diferencia entre 'no encontrado' (error de negocio) y 'error de conexión'
    (error técnico). La capa de infraestructura convierte esta excepción
    en un HTTP 404.
    """

    def __init__(self, product_id: int = None) -> None:
        """
        Inicializa el error con un mensaje descriptivo.

        Args:
            product_id (int, optional): ID del producto buscado. Si se provee,
                el mensaje incluye el ID para facilitar el debugging.
        """
        if product_id is not None:
            self.message = f"Producto con ID {product_id} no encontrado."
        else:
            self.message = "Producto no encontrado."
        super().__init__(self.message)


class InvalidProductDataError(Exception):
    """
    Se lanza cuando los datos de un producto no cumplen las reglas de negocio.

    Por ejemplo: precio negativo, stock inválido, nombre vacío.
    Se distingue de ValueError porque es específica del dominio del e-commerce.
    """

    def __init__(self, message: str = "Datos de producto inválidos.") -> None:
        """
        Args:
            message (str): Descripción del dato inválido. Tiene valor por defecto
                para uso rápido, pero siempre se recomienda ser específico.
        """
        self.message = message
        super().__init__(self.message)


class ChatServiceError(Exception):
    """
    Se lanza cuando hay un error al procesar un mensaje de chat.

    Puede originarse por fallas en el servicio de IA, errores de persistencia
    o datos de entrada inválidos. La capa de infraestructura la convierte en HTTP 500.
    """

    def __init__(self, message: str = "Error en el servicio de chat.") -> None:
        """
        Args:
            message (str): Descripción del error ocurrido.
        """
        self.message = message
        super().__init__(self.message)

"""Lee, en las respuestas HTTP de error, el código estable y los motivos.

El cuerpo solo trae el mensaje para quien usa el sistema; los programas leen el código en el
encabezado `X-Codigo-Error` y los motivos en `X-Motivos` (separados por `|`).
"""

from typing import Any


def codigo(respuesta: Any) -> str:
    return respuesta.headers["X-Codigo-Error"]


def motivos(respuesta: Any) -> list[str]:
    texto = respuesta.headers.get("X-Motivos", "")
    return texto.split("|") if texto else []

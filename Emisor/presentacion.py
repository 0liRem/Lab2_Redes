"""
Capa de PRESENTACION - lado EMISOR.
Servicio: codificar_mensaje
Codifica cada carácter del mensaje en su representación ASCII binaria
de 8 bits (ej. 'A' -> 01000001).
"""


def codificar_mensaje(texto: str) -> str:
    return "".join(format(ord(c), "08b") for c in texto)

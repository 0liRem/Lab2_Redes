from Emisor.fletcher import fletcher_checksum, pad_to_block
from Emisor.hamming import M_CODE, codificar_bloques_hamming

ALGO_FLETCHER = "0"
ALGO_HAMMING = "1"

HEADER_BITS = 16
BLOCK_CODE_BITS = 2
M_CODE_BITS = 2

BLOCK_CODE = {8: "00", 16: "01", 32: "10"}


def calcular_integridad(bits_mensaje: str, algoritmo: str, block_size: int) -> str:
    if algoritmo == "fletcher":
        return ALGO_FLETCHER + _calcular_fletcher(bits_mensaje, block_size)
    elif algoritmo == "hamming":
        return ALGO_HAMMING + _calcular_hamming(bits_mensaje, block_size)
    raise ValueError(f"Algoritmo desconocido: {algoritmo}")


def _calcular_fletcher(bits_mensaje: str, block_size: int) -> str:
    if block_size not in BLOCK_CODE:
        raise ValueError("Tamaño de bloque inválido para Fletcher")
    if len(bits_mensaje) >= (1 << HEADER_BITS):
        raise ValueError("Mensaje demasiado largo para el campo de longitud (16 bits)")

    codigo_bloque = BLOCK_CODE[block_size]
    header = format(len(bits_mensaje), "0{}b".format(HEADER_BITS))
    padded = pad_to_block(bits_mensaje, block_size)
    checksum = fletcher_checksum(padded, block_size)

    return codigo_bloque + header + padded + checksum


def _calcular_hamming(bits_mensaje: str, m: int) -> str:
    if m not in M_CODE:
        raise ValueError("Tamaño de bloque inválido para Hamming")
    if len(bits_mensaje) >= (1 << HEADER_BITS):
        raise ValueError("Mensaje demasiado largo para el campo de longitud (16 bits)")

    codigo_m = M_CODE[m]
    header = format(len(bits_mensaje), "0{}b".format(HEADER_BITS))
    bloques = codificar_bloques_hamming(bits_mensaje, m)

    return codigo_m + header + bloques


def corregir_mensaje(*_args, **_kwargs):
    # El emisor no corrige. Para Fletcher no aplica (solo detecta). Para
    # Hamming, la corrección real ocurre del lado del receptor dentro de
    # verificar_integridad (ver Receptor/enlace.js -> decodificarBloquesHamming),
    # que es donde se detecta y repara el bit alterado.
    return None
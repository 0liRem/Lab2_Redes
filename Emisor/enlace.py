

from Emisor.fletcher import fletcher_checksum, pad_to_block

HEADER_BITS = 16          # bits para indicar la longitud original del mensajes
BLOCK_CODE_BITS = 2       # bits para indicar el tamaño de bloque usado

BLOCK_CODE = {8: "00", 16: "01", 32: "10"}


def calcular_integridad(bits_mensaje: str, block_size: int) -> str:
    if block_size not in BLOCK_CODE:
        raise ValueError("Tamaño de bloque inválido")
    if len(bits_mensaje) >= (1 << HEADER_BITS):
        raise ValueError("Mensaje demasiado largo para el campo de longitud (16 bits)")

    codigo_bloque = BLOCK_CODE[block_size]
    header = format(len(bits_mensaje), "0{}b".format(HEADER_BITS))
    padded = pad_to_block(bits_mensaje, block_size)
    checksum = fletcher_checksum(padded, block_size)

    trama = codigo_bloque + header + padded + checksum
    return trama


def corregir_mensaje(*_args, **_kwargs):
    return None

"""
Implementación del algoritmo Fletcher checksum, generalizado para
bloques de 8, 16 o 32 bits.

Para una trama de longitud k (múltiplo del tamaño de bloque):
    sum1 = suma acumulada de cada bloque, mod (2^block_size - 1)
    sum2 = suma acumulada de sum1 en cada paso, mod (2^block_size - 1)

El checksum resultante tiene 2 * block_size bits: sum2 concatenado con sum1.
"""

BLOQUES_VALIDOS = (8, 16, 32)


def pad_to_block(bits: str, block_size: int) -> str:
    """Rellena la cadena de bits con ceros a la derecha hasta que su
    longitud sea múltiplo de block_size."""
    if block_size not in BLOQUES_VALIDOS:
        raise ValueError(f"Tamaño de bloque inválido: {block_size}")
    pad_len = (-len(bits)) % block_size
    return bits + "0" * pad_len


def fletcher_checksum(bits: str, block_size: int = 8) -> str:
    """
    Calcula el checksum Fletcher de una cadena de bits ya alineada
    (longitud múltiplo de block_size).

    Retorna una cadena binaria de longitud 2*block_size.
    """
    if block_size not in BLOQUES_VALIDOS:
        raise ValueError(f"Tamaño de bloque inválido: {block_size}")
    if len(bits) % block_size != 0:
        raise ValueError("La longitud de la trama debe ser múltiplo del bloque")

    mod = (1 << block_size) - 1  # 2^n - 1
    sum1 = 0
    sum2 = 0
    for i in range(0, len(bits), block_size):
        bloque = bits[i:i + block_size]
        valor = int(bloque, 2)
        sum1 = (sum1 + valor) % mod
        sum2 = (sum2 + sum1) % mod

    checksum = (sum2 << block_size) | sum1
    return format(checksum, "0{}b".format(block_size * 2))


if __name__ == "__main__":
    # Prueba rápida manual
    msg = "".join(format(ord(c), "08b") for c in "AB")
    for bs in BLOQUES_VALIDOS:
        padded = pad_to_block(msg, bs)
        cs = fletcher_checksum(padded, bs)
        print(f"block_size={bs:>2}  padded={padded}  checksum={cs}")

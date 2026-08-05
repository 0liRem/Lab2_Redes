M_CODE = {4: "00", 8: "01", 16: "10"}
CODE_TO_M = {v: k for k, v in M_CODE.items()}


def _es_potencia_de_dos(x: int) -> bool:
    return x > 0 and (x & (x - 1)) == 0


def calcular_r(m: int) -> int:
    """Menor r tal que m + r + 1 <= 2^r."""
    r = 1
    while (m + r + 1) > (1 << r):
        r += 1
    return r


def pad_to_m(bits: str, m: int) -> str:
    pad_len = (-len(bits)) % m
    return bits + "0" * pad_len


def encode_block(data_bits: str) -> str:
    """Codifica un bloque de m bits de datos en uno de n = m + r bits."""
    m = len(data_bits)
    r = calcular_r(m)
    n = m + r

    bits = [0] * (n + 1)  # 1-indexado, bits[0] no se usa
    it = iter(data_bits)
    for pos in range(1, n + 1):
        if not _es_potencia_de_dos(pos):
            bits[pos] = int(next(it))

    for i in range(r):
        p = 1 << i
        paridad = 0
        for pos in range(1, n + 1):
            if pos != p and (pos & p):
                paridad ^= bits[pos]
        bits[p] = paridad

    return "".join(str(b) for b in bits[1:])


def decode_block(block_bits: str, m: int):
    """Decodifica un bloque de n = m + r bits.

    Retorna (data_bits, hubo_error, corregido, sindrome).
    Un síndrome != 0 indica error; si cae dentro de 1..n se asume error
    de 1 bit y se corrige (limitación conocida de Hamming SEC: errores de
    2+ bits en el mismo bloque pueden no detectarse o corregirse mal).
    """
    r = calcular_r(m)
    n = m + r
    if len(block_bits) != n:
        return None, True, False, None

    bits = [0] + [int(b) for b in block_bits]

    sindrome = 0
    for i in range(r):
        p = 1 << i
        paridad = 0
        for pos in range(1, n + 1):
            if pos & p:
                paridad ^= bits[pos]
        if paridad != 0:
            sindrome |= p

    corregido = False
    if sindrome != 0 and 1 <= sindrome <= n:
        bits[sindrome] ^= 1
        corregido = True

    data_bits = "".join(
        str(bits[pos]) for pos in range(1, n + 1) if not _es_potencia_de_dos(pos)
    )
    hubo_error = sindrome != 0
    return data_bits, hubo_error, corregido, sindrome


def codificar_bloques_hamming(bits_mensaje: str, m: int) -> str:
    padded = pad_to_m(bits_mensaje, m)
    salida = []
    for i in range(0, len(padded), m):
        salida.append(encode_block(padded[i:i + m]))
    return "".join(salida)


def decodificar_bloques_hamming(trama_bits: str, m: int):
    """Decodifica todos los bloques de una trama Hamming.

    Retorna (data_bits_concatenados, hubo_algun_error, se_corrigieron_todos).
    """
    r = calcular_r(m)
    n = m + r
    if n == 0 or len(trama_bits) % n != 0:
        return None, True, False

    datos = []
    hubo_error = False
    todos_corregidos = True
    for i in range(0, len(trama_bits), n):
        bloque = trama_bits[i:i + n]
        data_bits, err, corregido, _ = decode_block(bloque, m)
        if data_bits is None:
            return None, True, False
        if err:
            hubo_error = True
            if not corregido:
                todos_corregidos = False
        datos.append(data_bits)

    return "".join(datos), hubo_error, todos_corregidos


if __name__ == "__main__":
    # Prueba rápida manual
    for m in (4, 8, 16):
        data = "1" * m
        enc = encode_block(data)
        print(f"m={m} r={calcular_r(m)} encoded={enc}")
        # Alterar un bit y verificar que se corrige
        alterado = list(enc)
        alterado[3] = "1" if alterado[3] == "0" else "0"
        alterado = "".join(alterado)
        recuperado, err, corregido, s = decode_block(alterado, m)
        print(f"  con error -> corregido={corregido} recuperado==original: {recuperado == data}")
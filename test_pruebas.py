import sys
import os
import random
import string
import csv

# test_pruebas.py está en la raíz del proyecto, al mismo nivel que Emisor/,
# así que basta con asegurar que esa raíz esté en el sys.path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Emisor.presentacion import codificar_mensaje
from Emisor.enlace import calcular_integridad, BLOCK_CODE
from Emisor.hamming import M_CODE, decodificar_bloques_hamming
from Emisor.ruido import aplicar_ruido
from Emisor.fletcher import fletcher_checksum

CODE_TO_BLOCK = {v: k for k, v in BLOCK_CODE.items()}
CODE_TO_M = {v: k for k, v in M_CODE.items()}
HEADER_BITS = 16
BLOCK_CODE_BITS = 2
M_CODE_BITS = 2

ALGO_FLETCHER = "0"
ALGO_HAMMING = "1"


def verificar_integridad_local(trama):
    """Réplica minimalista de la verificación del receptor, para pruebas.
    Retorna (ok, hubo_error, corregido)."""
    if not trama:
        return False, True, False

    algo_bit, resto = trama[0], trama[1:]

    if algo_bit == ALGO_FLETCHER:
        return _verificar_fletcher_local(resto)
    elif algo_bit == ALGO_HAMMING:
        return _verificar_hamming_local(resto)
    return False, True, False


def _verificar_fletcher_local(trama):
    codigo = trama[:BLOCK_CODE_BITS]
    block_size = CODE_TO_BLOCK.get(codigo)
    if block_size is None:
        return False, True, False
    header = trama[BLOCK_CODE_BITS:BLOCK_CODE_BITS + HEADER_BITS]
    original_len = int(header, 2)
    resto = trama[BLOCK_CODE_BITS + HEADER_BITS:]
    padded_len = ((original_len + block_size - 1) // block_size) * block_size
    padded = resto[:padded_len]
    checksum_recibido = resto[padded_len:padded_len + 2 * block_size]
    if len(padded) != padded_len or len(checksum_recibido) != 2 * block_size:
        return False, True, False
    checksum_calculado = fletcher_checksum(padded, block_size)
    ok = checksum_recibido == checksum_calculado
    return ok, not ok, False


def _verificar_hamming_local(trama):
    codigo_m = trama[:M_CODE_BITS]
    m = CODE_TO_M.get(codigo_m)
    if m is None:
        return False, True, False
    header = trama[M_CODE_BITS:M_CODE_BITS + HEADER_BITS]
    original_len = int(header, 2)  # noqa: F841 (se deja explícito para claridad)
    bloques = trama[M_CODE_BITS + HEADER_BITS:]
    data_bits, hubo_error, todos_corregidos = decodificar_bloques_hamming(bloques, m)
    if data_bits is None:
        return False, True, False
    ok = todos_corregidos
    corregido = hubo_error and todos_corregidos
    return ok, hubo_error, corregido


def mensaje_aleatorio(n_chars):
    return "".join(random.choice(string.ascii_letters + string.digits + " ") for _ in range(n_chars))


def experimento(n_chars, tasa_error, algoritmo, block_size, repeticiones=200):
    """Corre `repeticiones` envíos con los parámetros dados y devuelve
    estadísticas de detección/corrección de error y overhead."""
    detectados = 0
    no_detectados = 0
    corregidos = 0
    sin_error_real = 0
    overhead_bits = None
    total_bits = None

    for _ in range(repeticiones):
        texto = mensaje_aleatorio(n_chars)
        bits_msg = codificar_mensaje(texto)
        trama = calcular_integridad(bits_msg, algoritmo, block_size)

        if overhead_bits is None:
            overhead_bits = len(trama) - len(bits_msg)
            total_bits = len(trama)

        trama_ruido = aplicar_ruido(trama, tasa_error)

        hubo_alteracion = trama_ruido != trama
        ok, hubo_error_detectado, corregido = verificar_integridad_local(trama_ruido)

        if not hubo_alteracion:
            sin_error_real += 1
            continue

        if corregido:
            corregidos += 1
        elif ok:
            no_detectados += 1
        else:
            detectados += 1

    total_con_error_real = detectados + no_detectados + corregidos
    tasa_deteccion = ((detectados + corregidos) / total_con_error_real) if total_con_error_real else None
    tasa_correccion = (corregidos / total_con_error_real) if total_con_error_real else None

    return {
        "algoritmo": algoritmo,
        "n_chars": n_chars,
        "tasa_error": tasa_error,
        "block_size": block_size,
        "repeticiones": repeticiones,
        "overhead_bits": overhead_bits,
        "total_bits": total_bits,
        "overhead_pct": overhead_bits / total_bits * 100,
        "tramas_sin_alteracion": sin_error_real,
        "tramas_con_error_detectado": detectados,
        "tramas_con_error_corregido": corregidos,
        "tramas_con_error_no_detectado": no_detectados,
        "tasa_deteccion": tasa_deteccion,
        "tasa_correccion": tasa_correccion,
    }


def main():
    random.seed(42)
    resultados = []

    tamanos = [4, 8, 16, 32, 64, 128]
    tasas_error = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
    bloques_fletcher = [8, 16, 32]
    bloques_hamming = [4, 8, 16]

    algoritmos = [("fletcher", bloques_fletcher), ("hamming", bloques_hamming)]

    # Experimento 1: overhead vs tamaño de mensaje, por algoritmo/bloque
    for algoritmo, bloques in algoritmos:
        for bs in bloques:
            for n in tamanos:
                r = experimento(n, tasa_error=0.0, algoritmo=algoritmo, block_size=bs, repeticiones=1)
                resultados.append({"experimento": "overhead", **r})

    # Experimento 2: tasa de detección/corrección vs probabilidad de error
    for algoritmo, bloques in algoritmos:
        for bs in bloques:
            for te in tasas_error:
                r = experimento(n_chars=32, tasa_error=te, algoritmo=algoritmo, block_size=bs, repeticiones=300)
                resultados.append({"experimento": "deteccion", **r})

    # Experimento 3: tasa de detección/corrección vs tamaño de mensaje (tasa de error fija)
    for algoritmo, bloques in algoritmos:
        for bs in bloques:
            for n in tamanos:
                r = experimento(n_chars=n, tasa_error=0.02, algoritmo=algoritmo, block_size=bs, repeticiones=300)
                resultados.append({"experimento": "deteccion_vs_tamano", **r})

    out_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados.csv")
    campos = ["experimento", "algoritmo", "n_chars", "tasa_error", "block_size", "repeticiones",
              "overhead_bits", "total_bits", "overhead_pct",
              "tramas_sin_alteracion", "tramas_con_error_detectado", "tramas_con_error_corregido",
              "tramas_con_error_no_detectado", "tasa_deteccion", "tasa_correccion"]
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for r in resultados:
            writer.writerow(r)

    print(f"Resultados guardados en {out_csv} ({len(resultados)} filas)")
    return resultados


if __name__ == "__main__":
    main()
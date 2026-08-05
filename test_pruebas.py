

import sys
import os
import random
import string
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "emisor_python"))

from Emisor.presentacion import codificar_mensaje
from Emisor.enlace import calcular_integridad, BLOCK_CODE
from Emisor.ruido import aplicar_ruido
from Emisor.fletcher import fletcher_checksum

CODE_TO_BLOCK = {v: k for k, v in BLOCK_CODE.items()}
HEADER_BITS = 16
BLOCK_CODE_BITS = 2


def verificar_integridad_local(trama):
    """Réplica minimalista de la verificación del receptor, para pruebas."""
    codigo = trama[:BLOCK_CODE_BITS]
    block_size = CODE_TO_BLOCK.get(codigo)
    if block_size is None:
        return False
    header = trama[BLOCK_CODE_BITS:BLOCK_CODE_BITS + HEADER_BITS]
    original_len = int(header, 2)
    resto = trama[BLOCK_CODE_BITS + HEADER_BITS:]
    padded_len = ((original_len + block_size - 1) // block_size) * block_size
    padded = resto[:padded_len]
    checksum_recibido = resto[padded_len:padded_len + 2 * block_size]
    if len(padded) != padded_len or len(checksum_recibido) != 2 * block_size:
        return False
    checksum_calculado = fletcher_checksum(padded, block_size)
    return checksum_recibido == checksum_calculado


def mensaje_aleatorio(n_chars):
    return "".join(random.choice(string.ascii_letters + string.digits + " ") for _ in range(n_chars))


def experimento(n_chars, tasa_error, block_size, repeticiones=200):
    """Corre `repeticiones` envíos con los parámetros dados y devuelve
    estadísticas de detección de error y overhead."""
    detectados = 0
    no_detectados = 0
    sin_error_real = 0  
    overhead_bits = None
    total_bits = None

    for _ in range(repeticiones):
        texto = mensaje_aleatorio(n_chars)
        bits_msg = codificar_mensaje(texto)
        trama = calcular_integridad(bits_msg, block_size)

        if overhead_bits is None:
            overhead_bits = len(trama) - len(bits_msg)
            total_bits = len(trama)

        trama_ruido = aplicar_ruido(trama, tasa_error)

        hubo_alteracion = trama_ruido != trama
        ok = verificar_integridad_local(trama_ruido)

        if not hubo_alteracion:
            sin_error_real += 1
            continue

        if ok:
            no_detectados += 1  
        else:
            detectados += 1

    total_con_error_real = detectados + no_detectados
    tasa_deteccion = (detectados / total_con_error_real) if total_con_error_real else None

    return {
        "n_chars": n_chars,
        "tasa_error": tasa_error,
        "block_size": block_size,
        "repeticiones": repeticiones,
        "overhead_bits": overhead_bits,
        "total_bits": total_bits,
        "overhead_pct": overhead_bits / total_bits * 100,
        "tramas_sin_alteracion": sin_error_real,
        "tramas_con_error_detectado": detectados,
        "tramas_con_error_no_detectado": no_detectados,
        "tasa_deteccion": tasa_deteccion,
    }


def main():
    random.seed(42)
    resultados = []

    tamanos = [4, 8, 16, 32, 64, 128]
    tasas_error = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
    bloques = [8, 16, 32]

    #Experimento 1: overhead vs tamaño de mensaje, por bloque
    for bs in bloques:
        for n in tamanos:
            r = experimento(n, tasa_error=0.0, block_size=bs, repeticiones=1)
            resultados.append({"experimento": "overhead", **r})

    #Experimento 2: tasa de detección vs probabilidad de error, por bloque
    for bs in bloques:
        for te in tasas_error:
            r = experimento(n_chars=32, tasa_error=te, block_size=bs, repeticiones=300)
            resultados.append({"experimento": "deteccion", **r})

    #Experimento 3: tasa de detección vs tamaño de mensaje (tasa de error fija)
    for bs in bloques:
        for n in tamanos:
            r = experimento(n_chars=n, tasa_error=0.02, block_size=bs, repeticiones=300)
            resultados.append({"experimento": "deteccion_vs_tamano", **r})

    # Guardar CSV con todos los resultados
    out_csv = os.path.join(os.path.dirname(__file__), "resultados.csv")
    campos = ["experimento", "n_chars", "tasa_error", "block_size", "repeticiones",
              "overhead_bits", "total_bits", "overhead_pct",
              "tramas_sin_alteracion", "tramas_con_error_detectado",
              "tramas_con_error_no_detectado", "tasa_deteccion"]
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for r in resultados:
            writer.writerow(r)

    print(f"Resultados guardados en {out_csv} ({len(resultados)} filas)")
    return resultados


if __name__ == "__main__":
    main()

"""
Capa de RUIDO


Simula ruido 
"""

import random


def aplicar_ruido(bits: str, tasa_error: float) -> str:
    if tasa_error <= 0:
        return bits

    resultado = list(bits)
    for i in range(len(resultado)):
        if random.random() < tasa_error:
            resultado[i] = "1" if resultado[i] == "0" else "0"
    return "".join(resultado)

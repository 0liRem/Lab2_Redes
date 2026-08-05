BLOQUES_FLETCHER = (8, 16, 32)
BLOQUES_HAMMING = (4, 8, 16)


def solicitar_mensaje():
    # Mensaje a enviar
    print("Cajero Automático")
    texto = input("Ingrese el mensaje a enviar al servidor bancario: ")

    print("Algoritmos de integridad disponibles:")
    print("  1. fletcher  (detección de errores)")
    print("  2. hamming   (corrección de errores, SEC)")
    algoritmo = None
    while algoritmo not in ("fletcher", "hamming"):
        eleccion = input("Elija algoritmo [1/2] (1 por defecto): ").strip()
        if eleccion in ("", "1"):
            algoritmo = "fletcher"
        elif eleccion == "2":
            algoritmo = "hamming"
        else:
            print("Opción inválida.")

    bloques_validos = BLOQUES_FLETCHER if algoritmo == "fletcher" else BLOQUES_HAMMING
    block_size = None
    while block_size not in bloques_validos:
        entrada = input(
            f"Tamaño de bloque para {algoritmo} {bloques_validos} "
            f"({bloques_validos[0]} por defecto): "
        ).strip()
        if entrada == "":
            block_size = bloques_validos[0]
            break
        try:
            block_size = int(entrada)
        except ValueError:
            block_size = None
        if block_size not in bloques_validos:
            print(f"Valor inválido. Elija uno de {bloques_validos}.")

    entrada = input(
        "Tasa de error a simular en el canal (errores por bit de 0-1) "
        "[default 0]: "
    ).strip()
    tasa_error = float(entrada) if entrada else 0.0

    return texto, algoritmo, block_size, tasa_error
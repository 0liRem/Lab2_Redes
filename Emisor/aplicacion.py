

BLOQUES_VALIDOS = (8, 16, 32)


def solicitar_mensaje():
    #Mensaje a enviar 
    print("Cajero Automático")
    texto = input("Ingrese el mensaje a enviar al servidor bancario: ")

    print("Algoritmo de integridad disponible: fletcher (checksum)")
    algoritmo = "fletcher"

    block_size = None
    while block_size not in BLOQUES_VALIDOS:
        entrada = input("Tamaño de bloque para Fletcher [8/16/32] (8 por defecto): ").strip()
        if entrada == "":
            block_size = 8
            break
        try:
            block_size = int(entrada)
        except ValueError:
            block_size = None
        if block_size not in BLOQUES_VALIDOS:
            print("Valor inválido. Elija 8, 16 o 32.")

    entrada = input(
        "Tasa de error a simular en el canal (errores por bit de 0-1 ) "
        "[default 0]: "
    ).strip()
    tasa_error = float(entrada) if entrada else 0.0

    return texto, algoritmo, block_size, tasa_error

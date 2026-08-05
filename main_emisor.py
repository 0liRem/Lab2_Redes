"""
Aplicacion -> Presentacion -> Enlace -> Ruido -> Transmision

Ejecutar el server node main_receptor.py
"""

from Emisor.aplicacion import solicitar_mensaje
from Emisor.presentacion import codificar_mensaje
from Emisor.enlace import calcular_integridad
from Emisor.ruido import aplicar_ruido
from Emisor.transmision import enviar_informacion

HOST = "127.0.0.1"
PORT = 5656


def main():
    texto, algoritmo, block_size, tasa_error = solicitar_mensaje()

    #PRESENTACION 
    bits_mensaje = codificar_mensaje(texto)
    print(f"\n[PRESENTACION] Mensaje codificado ({len(bits_mensaje)} bits):")
    print(f"  {bits_mensaje}")

    #ENLACE
    trama = calcular_integridad(bits_mensaje, block_size)
    print(f"\n[ENLACE] Trama con checksum Fletcher-{block_size} ({len(trama)} bits):")
    print(f"  {trama}")
    overhead = len(trama) - len(bits_mensaje)
    print(f"  Overhead: {overhead} bits ({overhead/len(trama)*100:.1f}% de la trama)")

    #RUIDO
    trama_con_ruido = aplicar_ruido(trama, tasa_error)
    n_flips = sum(1 for a, b in zip(trama, trama_con_ruido) if a != b)
    print(f"\n[RUIDO] Tasa de error usada: {tasa_error}")
    print(f"[RUIDO] Bits alterados: {n_flips} / {len(trama)}")
    print(f"  Trama a transmitir: {trama_con_ruido}")

    #TRANSMISION
    try:
        enviar_informacion(HOST, PORT, trama_con_ruido)
        print(f"\n[TRANSMISION] Trama enviada a {HOST}:{PORT} (servidor bancario).")
    except ConnectionRefusedError:
        print(
            f"\n[TRANSMISION] ERROR: no se pudo conectar a {HOST}:{PORT}. "
            "¿Está corriendo el receptor (node main_receptor.js)?"
        )


if __name__ == "__main__":
    main()

import socket
import struct


def _bits_a_bytes(bits: str) -> bytes:
    n_bits = len(bits)
    n_bytes = (n_bits + 7) // 8
    bits_alineados = bits + "0" * (n_bytes * 8 - n_bits)
    data = bytearray()
    for i in range(0, len(bits_alineados), 8):
        data.append(int(bits_alineados[i:i + 8], 2))
    return bytes(data)


def enviar_informacion(host: str, port: int, bits: str) -> None:
    payload = _bits_a_bytes(bits)
    with socket.create_connection((host, port), timeout=5) as s:
        s.sendall(struct.pack("!I", len(bits)))
        s.sendall(payload)

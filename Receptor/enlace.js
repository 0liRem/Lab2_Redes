"use strict";


const { fletcherChecksum } = require("./fletcher");

const HEADER_BITS = 16;
const BLOCK_CODE_BITS = 2;
const CODE_TO_BLOCK = { "00": 8, "01": 16, "10": 32 };

function verificarIntegridad(trama) {
  if (trama.length < BLOCK_CODE_BITS + HEADER_BITS) {
    return { ok: false, mensajeBits: null, blockSize: null, motivo: "trama demasiado corta" };
  }

  const codigoBloque = trama.slice(0, BLOCK_CODE_BITS);
  const blockSize = CODE_TO_BLOCK[codigoBloque];
  if (!blockSize) {
    // El ruido corrompió el campo que identifica el tamaño de bloque.
    return { ok: false, mensajeBits: null, blockSize: null, motivo: "código de bloque corrupto" };
  }

  const header = trama.slice(BLOCK_CODE_BITS, BLOCK_CODE_BITS + HEADER_BITS);
  const originalLen = parseInt(header, 2);
  const resto = trama.slice(BLOCK_CODE_BITS + HEADER_BITS);

  const paddedLen = Math.ceil(originalLen / blockSize) * blockSize;
  const padded = resto.slice(0, paddedLen);
  const checksumRecibido = resto.slice(paddedLen, paddedLen + 2 * blockSize);

  if (padded.length !== paddedLen || checksumRecibido.length !== 2 * blockSize) {
    return { ok: false, mensajeBits: null, blockSize, motivo: "trama truncada/corrupta" };
  }

  const checksumCalculado = fletcherChecksum(padded, blockSize);
  const ok = checksumRecibido === checksumCalculado;
  const mensajeBits = padded.slice(0, originalLen);

  return { ok, mensajeBits, blockSize, motivo: ok ? null : "checksum no coincide" };
}

function corregirMensaje() {
  // Fletcher checksum solo detecta errores, no los corrige.
  return null;
}

module.exports = { verificarIntegridad, corregirMensaje };

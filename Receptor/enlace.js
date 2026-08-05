"use strict";

const { fletcherChecksum } = require("./fletcher");
const { CODE_TO_M, decodificarBloquesHamming } = require("./hamming");

const HEADER_BITS = 16;
const BLOCK_CODE_BITS = 2;
const M_CODE_BITS = 2;
const CODE_TO_BLOCK = { "00": 8, "01": 16, "10": 32 };

const ALGO_FLETCHER = "0";
const ALGO_HAMMING = "1";

function verificarIntegridad(trama) {
  if (trama.length < 1) {
    return {
      ok: false, mensajeBits: null, blockSize: null, algoritmo: null,
      corregido: false, motivo: "trama vacía",
    };
  }

  const algoBit = trama[0];
  const resto = trama.slice(1);

  if (algoBit === ALGO_FLETCHER) {
    return _verificarFletcher(resto);
  } else if (algoBit === ALGO_HAMMING) {
    return _verificarHamming(resto);
  }
  return {
    ok: false, mensajeBits: null, blockSize: null, algoritmo: null,
    corregido: false, motivo: "bit de algoritmo corrupto",
  };
}

function _verificarFletcher(trama) {
  if (trama.length < BLOCK_CODE_BITS + HEADER_BITS) {
    return {
      ok: false, mensajeBits: null, blockSize: null, algoritmo: "fletcher",
      corregido: false, motivo: "trama demasiado corta",
    };
  }

  const codigoBloque = trama.slice(0, BLOCK_CODE_BITS);
  const blockSize = CODE_TO_BLOCK[codigoBloque];
  if (!blockSize) {
    return {
      ok: false, mensajeBits: null, blockSize: null, algoritmo: "fletcher",
      corregido: false, motivo: "código de bloque corrupto",
    };
  }

  const header = trama.slice(BLOCK_CODE_BITS, BLOCK_CODE_BITS + HEADER_BITS);
  const originalLen = parseInt(header, 2);
  const resto = trama.slice(BLOCK_CODE_BITS + HEADER_BITS);

  const paddedLen = Math.ceil(originalLen / blockSize) * blockSize;
  const padded = resto.slice(0, paddedLen);
  const checksumRecibido = resto.slice(paddedLen, paddedLen + 2 * blockSize);

  if (padded.length !== paddedLen || checksumRecibido.length !== 2 * blockSize) {
    return {
      ok: false, mensajeBits: null, blockSize, algoritmo: "fletcher",
      corregido: false, motivo: "trama truncada/corrupta",
    };
  }

  const checksumCalculado = fletcherChecksum(padded, blockSize);
  const ok = checksumRecibido === checksumCalculado;
  const mensajeBits = padded.slice(0, originalLen);

  return {
    ok, mensajeBits, blockSize, algoritmo: "fletcher",
    corregido: false, motivo: ok ? null : "checksum no coincide",
  };
}

function _verificarHamming(trama) {
  if (trama.length < M_CODE_BITS + HEADER_BITS) {
    return {
      ok: false, mensajeBits: null, blockSize: null, algoritmo: "hamming",
      corregido: false, motivo: "trama demasiado corta",
    };
  }

  const codigoM = trama.slice(0, M_CODE_BITS);
  const m = CODE_TO_M[codigoM];
  if (!m) {
    return {
      ok: false, mensajeBits: null, blockSize: null, algoritmo: "hamming",
      corregido: false, motivo: "código de bloque corrupto",
    };
  }

  const header = trama.slice(M_CODE_BITS, M_CODE_BITS + HEADER_BITS);
  const originalLen = parseInt(header, 2);
  const bloques = trama.slice(M_CODE_BITS + HEADER_BITS);

  const { dataBits, huboError, todosCorregidos } = decodificarBloquesHamming(bloques, m);

  if (dataBits === null) {
    return {
      ok: false, mensajeBits: null, blockSize: m, algoritmo: "hamming",
      corregido: false, motivo: "trama truncada/corrupta",
    };
  }

  const mensajeBits = dataBits.slice(0, originalLen);
  // Hamming SEC corrige errores de 1 bit por bloque; si todos los bloques
  // con error se pudieron corregir, el mensaje final es confiable.
  const ok = todosCorregidos;

  return {
    ok,
    mensajeBits,
    blockSize: m,
    algoritmo: "hamming",
    corregido: huboError && todosCorregidos,
    motivo: ok
      ? (huboError ? "error corregido" : null)
      : "error no corregible (más de 1 bit alterado en un bloque)",
  };
}

function corregirMensaje() {
  return null;
}

module.exports = { verificarIntegridad, corregirMensaje };
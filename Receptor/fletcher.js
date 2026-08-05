"use strict";

const BLOQUES_VALIDOS = [8, 16, 32];

function padToBlock(bits, blockSize) {
  if (!BLOQUES_VALIDOS.includes(blockSize)) {
    throw new Error(`Tamaño de bloque inválido: ${blockSize}`);
  }
  const padLen = (blockSize - (bits.length % blockSize)) % blockSize;
  return bits + "0".repeat(padLen);
}

function fletcherChecksum(bits, blockSize = 8) {
  if (!BLOQUES_VALIDOS.includes(blockSize)) {
    throw new Error(`Tamaño de bloque inválido: ${blockSize}`);
  }
  if (bits.length % blockSize !== 0) {
    throw new Error("La longitud de la trama debe ser múltiplo del bloque");
  }

  const mod = (1n << BigInt(blockSize)) - 1n;
  let sum1 = 0n;
  let sum2 = 0n;

  for (let i = 0; i < bits.length; i += blockSize) {
    const bloque = bits.slice(i, i + blockSize);
    const valor = BigInt(parseInt(bloque, 2));
    sum1 = (sum1 + valor) % mod;
    sum2 = (sum2 + sum1) % mod;
  }

  const checksum = (sum2 << BigInt(blockSize)) | sum1;
  return checksum.toString(2).padStart(blockSize * 2, "0");
}

module.exports = { fletcherChecksum, padToBlock, BLOQUES_VALIDOS };

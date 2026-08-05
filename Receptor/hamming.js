"use strict";

/**
 * Código de Hamming (SEC - Single Error Correction), lado receptor.
 * Espejo de Emisor/hamming.py.
 */

const M_CODE = { 4: "00", 8: "01", 16: "10" };
const CODE_TO_M = { "00": 4, "01": 8, "10": 16 };

function esPotenciaDeDos(x) {
  return x > 0 && (x & (x - 1)) === 0;
}

function calcularR(m) {
  let r = 1;
  while (m + r + 1 > (1 << r)) {
    r += 1;
  }
  return r;
}

/**
 * Decodifica un bloque de n = m + r bits.
 * Retorna { dataBits, huboError, corregido, sindrome }.
 * Un síndrome != 0 indica error; si cae dentro de 1..n se asume error
 * de 1 bit y se corrige (limitación conocida de Hamming SEC: errores de
 * 2+ bits en el mismo bloque pueden no detectarse o corregirse mal).
 */
function decodeBlock(blockBits, m) {
  const r = calcularR(m);
  const n = m + r;
  if (blockBits.length !== n) {
    return { dataBits: null, huboError: true, corregido: false, sindrome: null };
  }

  const bits = [0];
  for (const c of blockBits) bits.push(c === "1" ? 1 : 0);

  let sindrome = 0;
  for (let i = 0; i < r; i++) {
    const p = 1 << i;
    let paridad = 0;
    for (let pos = 1; pos <= n; pos++) {
      if (pos & p) paridad ^= bits[pos];
    }
    if (paridad !== 0) sindrome |= p;
  }

  let corregido = false;
  if (sindrome !== 0 && sindrome >= 1 && sindrome <= n) {
    bits[sindrome] ^= 1;
    corregido = true;
  }

  let dataBits = "";
  for (let pos = 1; pos <= n; pos++) {
    if (!esPotenciaDeDos(pos)) dataBits += bits[pos];
  }

  return { dataBits, huboError: sindrome !== 0, corregido, sindrome };
}

/**
 * Decodifica todos los bloques de una trama Hamming.
 * Retorna { dataBits, huboError, todosCorregidos }.
 */
function decodificarBloquesHamming(tramaBits, m) {
  const r = calcularR(m);
  const n = m + r;
  if (n === 0 || tramaBits.length % n !== 0) {
    return { dataBits: null, huboError: true, todosCorregidos: false };
  }

  let datos = "";
  let huboError = false;
  let todosCorregidos = true;

  for (let i = 0; i < tramaBits.length; i += n) {
    const bloque = tramaBits.slice(i, i + n);
    const { dataBits, huboError: err, corregido } = decodeBlock(bloque, m);
    if (dataBits === null) {
      return { dataBits: null, huboError: true, todosCorregidos: false };
    }
    if (err) {
      huboError = true;
      if (!corregido) todosCorregidos = false;
    }
    datos += dataBits;
  }

  return { dataBits: datos, huboError, todosCorregidos };
}

module.exports = { M_CODE, CODE_TO_M, calcularR, decodeBlock, decodificarBloquesHamming };
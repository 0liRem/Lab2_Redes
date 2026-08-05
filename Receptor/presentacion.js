"use strict";

function decodificarMensaje(bits) {
  let texto = "";
  for (let i = 0; i + 8 <= bits.length; i += 8) {
    const byte = bits.slice(i, i + 8);
    texto += String.fromCharCode(parseInt(byte, 2));
  }
  return texto;
}

module.exports = { decodificarMensaje };

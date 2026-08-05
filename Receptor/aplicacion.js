"use strict";

function mostrarMensaje(texto, huboError) {
  console.log("=== Servidor Bancario (Receptor) ===");
  if (huboError) {
    console.log("⚠  ERROR: se detectaron errores de transmisión y no fue posible corregirlos.");
  } else {
    console.log(`Mensaje recibido correctamente: "${texto}"`);
  }
  console.log("");
}

module.exports = { mostrarMensaje };

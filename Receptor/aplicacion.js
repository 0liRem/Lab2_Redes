"use strict";

function mostrarMensaje(texto, huboError, corregido) {
  console.log("=== Servidor Bancario (Receptor) ===");
  if (huboError) {
    console.log("⚠  ERROR: se detectaron errores de transmisión y no fue posible corregirlos.");
  } else if (corregido) {
    console.log(`Mensaje recibido con error corregido: "${texto}"`);
  } else {
    console.log(`Mensaje recibido correctamente: "${texto}"`);
  }
  console.log("");
}

module.exports = { mostrarMensaje };
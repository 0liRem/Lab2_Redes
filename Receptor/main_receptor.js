"use strict";


const { iniciarServidor } = require("./transmision");
const { verificarIntegridad, corregirMensaje } = require("./enlace");
const { decodificarMensaje } = require("./presentacion");
const { mostrarMensaje } = require("./aplicacion");
const PORT = parseInt(process.argv[2] || "565", 10); /*PUERTO SI DA ERROR CAMBIARLO */

iniciarServidor(PORT, (trama, socket) => {
  console.log(`[TRANSMISION] Trama recibida (${trama.length} bits):`);
  console.log(`  ${trama}`);

  //ENLACE
  const { ok, mensajeBits, blockSize, motivo } = verificarIntegridad(trama);

  if (blockSize) {
    console.log(`\n[ENLACE] Tamaño de bloque detectado: Fletcher-${blockSize}`);
  }
  console.log(`[ENLACE] Verificación de integridad: ${ok ? "OK" : "ERROR DETECTADO"}${motivo ? ` (${motivo})` : ""}`);

  if (!ok) {
    // Fletcher 
    corregirMensaje();
    mostrarMensaje(null, true);
    socket.end();
    return;
  }

  // PRESENTACION 
  const texto = decodificarMensaje(mensajeBits);
  console.log(`\n[PRESENTACION] Mensaje decodificado: "${texto}"`);

  // APLICACION 
  mostrarMensaje(texto, false);

  socket.end();
});

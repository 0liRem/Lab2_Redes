"use strict";

const net = require("net");

function iniciarServidor(port, onFrame) {
  const server = net.createServer((socket) => {
    let buffer = Buffer.alloc(0);
    let bitLen = null;
    let expectedBytes = null;

    socket.on("data", (chunk) => {
      buffer = Buffer.concat([buffer, chunk]);

      if (bitLen === null && buffer.length >= 4) {
        bitLen = buffer.readUInt32BE(0);
        expectedBytes = Math.ceil(bitLen / 8);
      }

      if (bitLen !== null && buffer.length >= 4 + expectedBytes) {
        const frameBytes = buffer.slice(4, 4 + expectedBytes);
        let bits = "";
        for (const b of frameBytes) {
          bits += b.toString(2).padStart(8, "0");
        }
        bits = bits.slice(0, bitLen);
        onFrame(bits, socket);

        buffer = Buffer.alloc(0);
        bitLen = null;
        expectedBytes = null;
      }
    });

    socket.on("error", (err) => {
      console.error("[TRANSMISION] Error de socket:", err.message);
    });
  });

  server.listen(port, () => {
    console.log(`[TRANSMISION] Servidor bancario escuchando en el puerto ${port}...\n`);
  });

  return server;
}

module.exports = { iniciarServidor };

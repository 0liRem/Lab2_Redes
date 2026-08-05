# Laboratorio 2 - Esquemas de Detección y Corrección de Errores

## Descripción

Este proyecto corresponde al Laboratorio 2 del curso **CC3067 - Redes** de la Universidad del Valle de Guatemala.

Se implementó una arquitectura por capas para simular la comunicación entre un **cajero automático (emisor)** y un **servidor bancario (receptor)** a través de un canal no confiable. El sistema incorpora mecanismos de detección y corrección de errores mediante los algoritmos **Fletcher Checksum** y **Código de Hamming (SEC)**.

El emisor fue desarrollado en **Python**, mientras que el receptor fue implementado en **Node.js**, cumpliendo con el requisito de utilizar dos lenguajes de programación diferentes.

---

## Características

- Arquitectura basada en capas:
  - Aplicación
  - Presentación
  - Enlace
  - Ruido
  - Transmisión
- Comunicación mediante sockets TCP.
- Simulación de ruido con probabilidad configurable.
- Implementación de Fletcher Checksum para detección de errores.
- Implementación del Código de Hamming (SEC) para detección y corrección de errores de un bit.
- Generación automática de pruebas experimentales.
- Generación automática de gráficas para el análisis de resultados.

---

## Estructura del proyecto

```
.
├── Emisor/
│   ├── aplicacion.py
│   ├── presentacion.py
│   ├── enlace.py
│   ├── fletcher.py
│   ├── hamming.py
│   ├── ruido.py
│   └── transmision.py
│
├── Receptor/
│   ├── aplicacion.js
│   ├── presentacion.js
│   ├── enlace.js
│   ├── fletcher.js
│   ├── hamming.js
│   └── transmision.js
│
├── main_emisor.py
├── main_receptor.js
├── test_pruebas.py
├── graficar_resultados.py
├── resultados.csv
└── README.md
```

---

## Arquitectura

El flujo de comunicación implementado es el siguiente:

```
EMISOR (Python)

Aplicación
      ↓
Presentación
      ↓
Enlace
      ↓
Ruido
      ↓
Transmisión (TCP)

================ Canal =================

Transmisión
      ↓
Enlace
      ↓
Presentación
      ↓
Aplicación

RECEPTOR (Node.js)
```

---

## Algoritmos implementados

### Fletcher Checksum

Algoritmo de detección de errores basado en dos sumas acumulativas módulo \(2^n-1\).

Características:

- Bloques de 8, 16 y 32 bits.
- Padding automático.
- Detección de errores mediante checksum.
- No posee capacidad de corrección.

---

### Código de Hamming (SEC)

Implementación del código de Hamming con capacidad de corregir un único error por bloque.

Características:

- Bloques de datos de 4, 8 y 16 bits.
- Cálculo automático de bits de paridad.
- Detección de errores.
- Corrección de un error por bloque.
- Si existen múltiples errores dentro de un mismo bloque, únicamente se reporta que el mensaje no puede corregirse.

---

## Requisitos

### Python

- Python 3.10 o superior

Bibliotecas utilizadas:

- socket
- random
- csv
- matplotlib

Instalación:

```bash
pip install matplotlib
```

### Node.js

- Node.js 18 o superior

No se requieren dependencias externas.

---

## Ejecución

### 1. Iniciar el receptor

```bash
node main_receptor.js
```

---

### 2. Ejecutar el emisor

```bash
python main_emisor.py
```

Durante la ejecución el programa solicitará:

- Mensaje
- Algoritmo (Fletcher o Hamming)
- Tamaño del bloque
- Tasa de error del canal

---

## Pruebas automáticas

Para ejecutar todas las pruebas experimentales:

```bash
python test_pruebas.py
```

Este programa genera el archivo:

```
resultados.csv
```

---

## Generación de gráficas

A partir de los resultados experimentales:

```bash
python graficar_resultados.py
```

Se generan automáticamente las gráficas utilizadas en el reporte:

- Overhead vs. tamaño del mensaje
- Tasa de detección vs. tasa de error
- Tasa de corrección de Hamming
- Detección vs. tamaño del mensaje
- Comparación de overhead entre Fletcher y Hamming

---

## Funcionamiento

1. El usuario ingresa un mensaje.
2. El mensaje se codifica en ASCII binario.
3. La capa de enlace agrega la información de integridad correspondiente.
4. Se introduce ruido según una probabilidad configurada.
5. La trama se transmite mediante sockets TCP.
6. El receptor verifica la integridad.
7. Si el algoritmo lo permite, corrige errores.
8. El mensaje se decodifica y se muestra al usuario.

---

## Autores

- Oliver Viau - 23544
- Osman de León - 23428

Curso: **CC3067 - Redes**

Universidad del Valle de Guatemala
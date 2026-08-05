import csv
import os
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def cargar_resultados(ruta_csv):
    with open(ruta_csv, newline="") as f:
        rows = list(csv.DictReader(f))

    def num(v):
        if v is None or v == "":
            return None
        return float(v)

    for r in rows:
        r["n_chars"] = int(num(r["n_chars"]))
        r["block_size"] = int(num(r["block_size"]))
        r["tasa_error"] = num(r["tasa_error"])
        r["overhead_pct"] = num(r["overhead_pct"])
        r["tasa_deteccion"] = num(r["tasa_deteccion"])
        r["tasa_correccion"] = num(r["tasa_correccion"])
    return rows


def agrupar(rows, filtro, x_key, y_key, serie_key):
    """Devuelve {valor_serie: [(x, y), ...]} ordenado por x."""
    series = defaultdict(list)
    for r in rows:
        if not filtro(r):
            continue
        if r[y_key] is None:
            continue
        series[r[serie_key]].append((r[x_key], r[y_key]))
    for k in series:
        series[k].sort(key=lambda t: t[0])
    return dict(sorted(series.items()))


def grafica_overhead_vs_tamano(rows, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, algoritmo in zip(axes, ("fletcher", "hamming")):
        series = agrupar(
            rows,
            lambda r: r["experimento"] == "overhead" and r["algoritmo"] == algoritmo,
            "n_chars", "overhead_pct", "block_size",
        )
        for block_size, puntos in series.items():
            xs = [p[0] for p in puntos]
            ys = [p[1] for p in puntos]
            etiqueta = f"bloque={block_size}"
            ax.plot(xs, ys, marker="o", label=etiqueta)
        ax.set_title(algoritmo.capitalize())
        ax.set_xlabel("Tamaño del mensaje (caracteres)")
        ax.set_ylabel("Overhead (%)")
        ax.legend()
        ax.grid(True, alpha=0.3)
    fig.suptitle("Overhead vs. tamaño del mensaje")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "01_overhead_vs_tamano.png"), dpi=150)
    plt.close(fig)


def grafica_deteccion_vs_tasa_error(rows, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, algoritmo in zip(axes, ("fletcher", "hamming")):
        series = agrupar(
            rows,
            lambda r: r["experimento"] == "deteccion" and r["algoritmo"] == algoritmo,
            "tasa_error", "tasa_deteccion", "block_size",
        )
        for block_size, puntos in series.items():
            xs = [p[0] for p in puntos]
            ys = [p[1] * 100 for p in puntos]
            ax.plot(xs, ys, marker="o", label=f"bloque={block_size}")
        ax.set_title(algoritmo.capitalize())
        ax.set_xlabel("Tasa de error del canal")
        ax.set_ylabel("Tasa de detección (%)")
        ax.set_ylim(-5, 105)
        ax.legend()
        ax.grid(True, alpha=0.3)
    fig.suptitle("Tasa de detección de errores vs. tasa de error del canal")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "02_deteccion_vs_tasa_error.png"), dpi=150)
    plt.close(fig)


def grafica_correccion_hamming(rows, out_dir):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    series = agrupar(
        rows,
        lambda r: r["experimento"] == "deteccion" and r["algoritmo"] == "hamming",
        "tasa_error", "tasa_correccion", "block_size",
    )
    for block_size, puntos in series.items():
        xs = [p[0] for p in puntos]
        ys = [p[1] * 100 for p in puntos]
        ax.plot(xs, ys, marker="o", label=f"m={block_size}")
    ax.set_title("Tasa de corrección (Hamming) vs. tasa de error del canal")
    ax.set_xlabel("Tasa de error del canal")
    ax.set_ylabel("Tasa de corrección (%)")
    ax.set_ylim(-5, 105)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "03_correccion_hamming.png"), dpi=150)
    plt.close(fig)


def grafica_deteccion_vs_tamano(rows, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, algoritmo in zip(axes, ("fletcher", "hamming")):
        series = agrupar(
            rows,
            lambda r: r["experimento"] == "deteccion_vs_tamano" and r["algoritmo"] == algoritmo,
            "n_chars", "tasa_deteccion", "block_size",
        )
        for block_size, puntos in series.items():
            xs = [p[0] for p in puntos]
            ys = [p[1] * 100 for p in puntos]
            ax.plot(xs, ys, marker="o", label=f"bloque={block_size}")
        ax.set_title(algoritmo.capitalize())
        ax.set_xlabel("Tamaño del mensaje (caracteres)")
        ax.set_ylabel("Tasa de detección (%)")
        ax.set_ylim(-5, 105)
        ax.legend()
        ax.grid(True, alpha=0.3)
    fig.suptitle("Tasa de detección vs. tamaño del mensaje (tasa de error fija)")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "04_deteccion_vs_tamano.png"), dpi=150)
    plt.close(fig)


def grafica_comparacion_overhead(rows, out_dir, n_chars_ref=32):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    puntos = defaultdict(dict)
    for r in rows:
        if r["experimento"] == "overhead" and r["n_chars"] == n_chars_ref:
            puntos[r["algoritmo"]][r["block_size"]] = r["overhead_pct"]

    algoritmos = ["fletcher", "hamming"]
    ancho = 0.35
    todos_bloques = sorted({bs for d in puntos.values() for bs in d})
    x = range(len(todos_bloques))

    for i, algoritmo in enumerate(algoritmos):
        offset = (i - 0.5) * ancho
        xs, ys = [], []
        for xi, bs in zip(x, todos_bloques):
            val = puntos[algoritmo].get(bs)
            if val is not None:
                xs.append(xi + offset)
                ys.append(val)
        ax.bar(xs, ys, width=ancho, label=algoritmo.capitalize())

    ax.set_xticks(list(x))
    ax.set_xticklabels([str(bs) for bs in todos_bloques])
    ax.set_xlabel("Tamaño de bloque")
    ax.set_ylabel("Overhead (%)")
    ax.set_title(f"Overhead: Fletcher vs. Hamming (mensaje de {n_chars_ref} caracteres)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "05_comparacion_overhead.png"), dpi=150)
    plt.close(fig)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = sys.argv[1] if len(sys.argv) > 1 else os.path.join(script_dir, "resultados.csv")

    if not os.path.exists(ruta_csv):
        print(f"No se encontró {ruta_csv}. Corré primero test_pruebas.py.")
        sys.exit(1)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(ruta_csv)), "graficas")
    os.makedirs(out_dir, exist_ok=True)

    rows = cargar_resultados(ruta_csv)

    grafica_overhead_vs_tamano(rows, out_dir)
    grafica_deteccion_vs_tasa_error(rows, out_dir)
    grafica_correccion_hamming(rows, out_dir)
    grafica_deteccion_vs_tamano(rows, out_dir)
    grafica_comparacion_overhead(rows, out_dir)

    print(f"Gráficas guardadas en: {out_dir}")


if __name__ == "__main__":
    main()
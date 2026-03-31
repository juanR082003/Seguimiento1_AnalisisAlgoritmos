from __future__ import annotations
"""CLI de entrada del proyecto.

Flujo de alto nivel:
1) Python carga este modulo y evalua el bloque __main__.
2) main() parsea argumentos (--years, --benchmark-size).
3) main() delega toda la logica a src.app.run_pipeline().

Este archivo no contiene logica de negocio para mantener clara la separacion
entre interfaz de ejecucion (CLI) y procesamiento (pipeline).
"""

import argparse
from pathlib import Path

from src.app import run_pipeline
from src.config import DEFAULT_BENCHMARK_SIZE, DEFAULT_YEARS


def main() -> None:
    """Punto de entrada invocado al ejecutar python main.py ...

argparse interpreta los argumentos de linea de comandos y entrega los valores
tipados en args. Luego se resuelve base_dir y se ejecuta run_pipeline.
    """
    parser = argparse.ArgumentParser(description="Proyecto de análisis algorítmico financiero")
    parser.add_argument("--years", type=int, default=DEFAULT_YEARS, help="Años de histórico a descargar")
    parser.add_argument("--benchmark-size", type=int, default=DEFAULT_BENCHMARK_SIZE, help="Cantidad de enteros para comparar tiempos de ordenamiento",
)
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    run_pipeline(base_dir=base_dir, years=args.years, benchmark_size=args.benchmark_size)
    print("Proceso completado. Revisa data/ y outputs/.")


if __name__ == "__main__":
    main()

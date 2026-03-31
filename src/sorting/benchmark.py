from __future__ import annotations
"""Benchmark de algoritmos de ordenamiento sobre datos enteros.

Cada algoritmo se valida contra una referencia esperada y se mide por mediana
de tiempos para reducir ruido de ejecucion.
"""

import statistics
import time
from typing import Callable

from src.config import COMPLEXITIES
from src.sorting.algorithms import (
    binary_insertion_sort,
    bitonic_sort,
    bucket_sort,
    comb_sort,
    gnome_sort,
    heap_sort,
    pigeonhole_sort,
    quick_sort,
    radix_sort,
    selection_sort,
    timsort_algo,
    tree_sort,
)


def benchmark_algorithms(int_data: list[int], runs: int = 3) -> list[dict[str, object]]:
    """Ejecuta y valida los 12 algoritmos solicitados.

Args:
    int_data: Lista de enteros a ordenar.
    runs: Numero de repeticiones por algoritmo.

Returns:
    Lista de resultados con metodo, tamano, complejidad y tiempo.
    """
    funcs: list[tuple[str, Callable[[list[int]], list[int]]]] = [
        ("TimSort", timsort_algo),
        ("Comb Sort", comb_sort),
        ("Selection Sort", selection_sort),
        ("Tree Sort", tree_sort),
        ("Pigeonhole Sort", pigeonhole_sort),
        ("Bucket Sort", bucket_sort),
        ("QuickSort", quick_sort),
        ("HeapSort", heap_sort),
        ("Bitonic Sort", bitonic_sort),
        ("Gnome Sort", gnome_sort),
        ("Binary Insertion Sort", binary_insertion_sort),
        ("RadixSort", radix_sort),
    ]

    expected = sorted(int_data)
    results: list[dict[str, object]] = []

    for name, func in funcs:
        timings: list[float] = []

        for _ in range(runs):
            t0 = time.perf_counter()
            output = func(int_data)
            elapsed = time.perf_counter() - t0

            if output != expected:
                # Falla rapida: evita reportar tiempos de una implementacion incorrecta.
                raise RuntimeError(f"{name} no produjo orden correcto")

            timings.append(elapsed)

        results.append(
            {
                "method": name,
                "size": len(int_data),
                "complexity": COMPLEXITIES[name],
                "time_seconds": statistics.median(timings),
            }
        )

    return results

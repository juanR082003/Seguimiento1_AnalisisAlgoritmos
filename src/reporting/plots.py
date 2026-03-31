from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def save_bar_plot(results: list[dict[str, object]], path: Path) -> None:
    ordered = sorted(results, key=lambda x: x["time_seconds"])
    methods = [str(row["method"]) for row in ordered]
    times = [float(row["time_seconds"]) for row in ordered]

    plt.figure(figsize=(12, 6))
    plt.bar(methods, times)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Tiempo (s)")
    plt.title("Comparación de tiempos de ordenamiento (ascendente)")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()

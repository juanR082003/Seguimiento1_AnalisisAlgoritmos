from __future__ import annotations
"""Funciones de salida para persistir resultados y artefactos del pipeline."""

import csv
import json
from pathlib import Path

from src.domain.models import PriceRow


PRICE_HEADER = ["asset", "date", "open", "high", "low", "close", "volume", "is_imputed", "source"]


def ensure_dirs(base_dir: Path) -> dict[str, Path]:
    """Crea (si no existen) las carpetas de trabajo y retorna sus rutas."""
    data_raw = base_dir / "data" / "raw"
    data_processed = base_dir / "data" / "processed"
    outputs = base_dir / "outputs"

    for path in (data_raw, data_processed, outputs):
        path.mkdir(parents=True, exist_ok=True)

    return {"raw": data_raw, "processed": data_processed, "outputs": outputs}


def write_price_rows(path: Path, rows: list[PriceRow]) -> None:
    """Escribe filas de precios en CSV con cabecera estandar."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(PRICE_HEADER)
        for row in rows:
            writer.writerow(row.to_csv_row())


def save_table(results: list[dict[str, object]], path: Path) -> None:
    """Guarda la Tabla 1 (metodo, tamano, complejidad, tiempo) en CSV."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["metodo", "tamano", "complejidad", "tiempo_segundos"])
        for row in results:
            writer.writerow([row["method"], row["size"], row["complexity"], f"{row['time_seconds']:.8f}"])


def save_markdown_summary(results: list[dict[str, object]], path: Path) -> None:
    """Guarda resumen de la Tabla 1 en formato Markdown."""
    ordered = sorted(results, key=lambda x: x["time_seconds"])
    lines = [
        "# Tabla 1 - Análisis de datos enteros",
        "",
        "| Método de ordenamiento | Tamaño | Complejidad | Tiempo (s) |",
        "|---|---:|---|---:|",
    ]

    for row in ordered:
        lines.append(
            f"| {row['method']} | {row['size']} | {row['complexity']} | {float(row['time_seconds']):.8f} |"
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def write_metadata(path: Path, metadata: dict[str, object]) -> None:
    """Persiste metadatos de ejecucion para trazabilidad y reproducibilidad."""
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def top_15_volume_days(rows: list[PriceRow]) -> list[PriceRow]:
    """Retorna los 15 registros con mayor volumen, ordenados ascendentemente."""
    highest = sorted(rows, key=lambda row: row.volume, reverse=True)[:15]
    return sorted(highest, key=lambda row: row.volume)

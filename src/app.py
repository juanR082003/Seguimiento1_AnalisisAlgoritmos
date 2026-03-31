from __future__ import annotations
"""Orquestador principal del proyecto.

Este modulo coordina el flujo completo: ETL, unificacion, benchmark y reportes.
Es el siguiente paso natural despues de main.py.

Flujo resumido:
1) Extrae historicos de ETFs/activos por HTTP.
2) Limpia valores faltantes y normaliza OHLCV.
3) Unifica calendario entre activos.
4) Ejecuta benchmark de 12 algoritmos de ordenamiento.
5) Genera archivos finales de salida.
"""

import datetime as dt
import random
from pathlib import Path

from src.config import ASSETS
from src.etl.cleaner import clean_asset_rows
from src.etl.downloader import fetch_asset_csv
from src.etl.unifier import sort_records_by_date_close, to_sort_key_int, unify_assets
from src.reporting.plots import save_bar_plot
from src.reporting.writers import (
    ensure_dirs,
    save_markdown_summary,
    save_table,
    top_15_volume_days,
    write_metadata,
    write_price_rows,
)
from src.sorting.benchmark import benchmark_algorithms


def run_pipeline(base_dir: Path, years: int, benchmark_size: int) -> None:
    """Ejecuta el pipeline completo de extremo a extremo.

Args:
    base_dir: Ruta raiz del proyecto.
    years: Ventana historica en anos para filtrar datos de mercado.
        Ejemplo: years=5 toma aproximadamente los ultimos 5 anos de datos.
    benchmark_size: Numero de enteros usados para comparar algoritmos.
        Ejemplo: benchmark_size=1200 significa que se toman 1200 claves
        enteras derivadas del dataset unificado para medir tiempos.

Orden de ejecucion:
    1) Prepara carpetas de salida.
    2) Descarga y limpia datos por activo.
    3) Unifica series en un calendario comun y ordena registros.
    4) Convierte registros a enteros para benchmark.
    5) Ejecuta 12 algoritmos, mide tiempos y genera reportes.
    6) Calcula top 15 por volumen y guarda metadata.
    """
    paths = ensure_dirs(base_dir)

    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=365 * years)

    cleaned_by_asset = {}
    for asset in ASSETS:
        # ETL por activo: extraer -> limpiar -> validar que queden filas utiles.
        raw_rows = fetch_asset_csv(asset, start_date, paths["raw"])
        cleaned_rows = clean_asset_rows(asset, raw_rows)
        if not cleaned_rows:
            raise RuntimeError(f"{asset} no tiene filas válidas tras limpieza")
        cleaned_by_asset[asset] = cleaned_rows

    unified = unify_assets(cleaned_by_asset)
    unified_sorted = sort_records_by_date_close(unified)

    write_price_rows(paths["processed"] / "dataset_unificado.csv", unified_sorted)

    key_ints = [to_sort_key_int(row) for row in unified_sorted]
    unique_sorted = sorted(set(key_ints))
    rank_map = {value: idx for idx, value in enumerate(unique_sorted)}
    # benchmark_size controla cuantas observaciones entran al benchmark.
    # Si usas 1200, se comparan los 12 algoritmos sobre 1200 enteros.
    benchmark_input = [rank_map[x] for x in key_ints[:benchmark_size]]
    # Semilla fija para reproducir la misma mezcla en cada corrida.
    random.Random(42).shuffle(benchmark_input)

    if len(benchmark_input) < 64:
        raise RuntimeError("benchmark_size demasiado pequeño para comparar algoritmos")

    results = benchmark_algorithms(benchmark_input, runs=3)
    save_table(results, paths["outputs"] / "tabla1_tiempos.csv")
    save_markdown_summary(results, paths["outputs"] / "tabla1_tiempos.md")
    save_bar_plot(results, paths["outputs"] / "barras_tiempos_ordenamiento.png")

    top15 = top_15_volume_days(unified_sorted)
    write_price_rows(paths["outputs"] / "top15_mayor_volumen_asc.csv", top15)

    metadata = {
        "assets": ASSETS,
        "date_start": start_date.isoformat(),
        "date_end": end_date.isoformat(),
        "total_rows_unified": len(unified_sorted),
        "benchmark_size": len(benchmark_input),
        "note": "Para mantener viabilidad computacional en algoritmos O(n^2), la tabla de tiempos usa un subconjunto del dataset unificado.",
    }
    write_metadata(paths["outputs"] / "metadata.json", metadata)

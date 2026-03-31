from __future__ import annotations
"""Extraccion de datos historicos por HTTP.

La fuente se consulta con URL construida manualmente por activo. Se implementa
control de errores, reintentos y persistencia del CSV crudo para trazabilidad.

Donde se hace la extraccion de ETFs:
- En fetch_asset_csv(), al construir la URL y ejecutar requests.get().

Por que esta API publica (Stooq):
- Responde en CSV directo (facil de auditar y parsear manualmente).
- Permite consulta por simbolo sin librerias financieras de alto nivel.
- Es compatible con la restriccion del curso: peticiones HTTP explicitas.
"""

import datetime as dt
import time
import csv
from pathlib import Path

import requests


def _filter_rows_since(rows: list[dict[str, str]], start_date: dt.date) -> list[dict[str, str]]:
    """Filtra filas con fecha valida mayores o iguales a start_date."""
    filtered: list[dict[str, str]] = []
    for row in rows:
        try:
            row_date = dt.date.fromisoformat(row["Date"])
        except Exception:
            continue
        if row_date >= start_date:
            filtered.append(row)
    return filtered


def fetch_asset_csv(asset: str, start_date: dt.date, out_dir: Path) -> list[dict[str, str]]:
    """Descarga y parsea el historico diario de un activo.

Args:
    asset: Ticker (ej. SPY, VOO).
    start_date: Fecha minima incluida en el resultado.
    out_dir: Carpeta donde se guarda el CSV crudo descargado.

Returns:
    Lista de filas CSV (dict) filtradas desde start_date.
    Campos esperados por fila: Date, Open, High, Low, Close, Volume.

Raises:
    RuntimeError: Si falla la descarga tras 3 intentos.
    """
    symbol = f"{asset.lower()}.us"
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    csv_path = out_dir / f"{asset}.csv"
    last_error: Exception | None = None

    for _ in range(3):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            text = response.text.strip()
            if not text or text.startswith("No data"):
                raise ValueError(f"Sin datos para {asset} en Stooq")

            # Guardar crudo en CSV facilita trazabilidad y reproducibilidad:
            # se puede inspeccionar exactamente lo recibido de la API.
            csv_path.write_text(text, encoding="utf-8")

            rows = list(csv.DictReader(text.splitlines()))
            filtered_rows = _filter_rows_since(rows, start_date)
            if filtered_rows:
                return filtered_rows
            raise ValueError(f"Descarga de {asset} sin filas validas desde {start_date.isoformat()}")
        except Exception as exc:
            last_error = exc
            time.sleep(1)

    if csv_path.exists():
        text = csv_path.read_text(encoding="utf-8").strip()
        if text:
            rows = list(csv.DictReader(text.splitlines()))
            filtered_rows = _filter_rows_since(rows, start_date)
            if filtered_rows:
                return filtered_rows

    raise RuntimeError(
        f"No fue posible descargar {asset}: {last_error}. "
        "Tampoco se encontro un CSV local util en data/raw."
    )

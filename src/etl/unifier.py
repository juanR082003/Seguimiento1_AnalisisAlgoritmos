from __future__ import annotations
"""Unificacion de activos en calendario comun y utilidades de ordenamiento.

Librerias y dependencias usadas:
- datetime (dt): manejo de fechas para llaves temporales.
- PriceRow: modelo tipado de una fila financiera.

Objetivo del modulo:
- Alinear series de distintos activos al mismo calendario.
- Preparar ordenamientos requeridos por fecha y cierre.
- Convertir filas a clave entera para benchmark.
"""

import datetime as dt

from src.domain.models import PriceRow


def unify_assets(cleaned_by_asset: dict[str, list[PriceRow]]) -> list[PriceRow]:
    """Alinea todos los activos al mismo calendario de fechas.

Si un activo no tiene dato en una fecha del calendario union, se genera un
registro imputado por arrastre del cierre previo (forward fill).

Esto permite comparar todos los activos en una misma linea de tiempo.
    """
    calendar = sorted({row.date for rows in cleaned_by_asset.values() for row in rows})
    unified: list[PriceRow] = []

    for asset, rows in cleaned_by_asset.items():
        by_date = {row.date: row for row in rows}
        first_close = rows[0].close if rows else 0.0
        previous_close = first_close

        for date in calendar:
            observed = by_date.get(date)
            if observed is not None:
                previous_close = observed.close
                unified.append(observed)
                continue

            fill = previous_close if previous_close > 0 else first_close
            unified.append(
                PriceRow(
                    asset=asset,
                    date=date,
                    open=fill,
                    high=fill,
                    low=fill,
                    close=fill,
                    volume=0,
                    is_imputed=1,
                    source="calendar_alignment",
                )
            )

    return unified


def sort_records_by_date_close(rows: list[PriceRow]) -> list[PriceRow]:
    """Ordena ascendente por (fecha, close), como exige el requerimiento."""
    return sorted(rows, key=lambda row: (row.date, row.close))


def to_sort_key_int(row: PriceRow) -> int:
    """Convierte un PriceRow a entero comparable para benchmarking.

La clave combina fecha (yyyymmdd) y close escalado a 4 decimales.

Motivo:
- Los algoritmos del benchmark trabajan sobre enteros.
- Esta representacion conserva el orden por fecha y luego por close.
    """
    date_key = row.date.year * 10000 + row.date.month * 100 + row.date.day
    close_key = int(round(row.close * 10000))
    return date_key * 10_000_000 + close_key

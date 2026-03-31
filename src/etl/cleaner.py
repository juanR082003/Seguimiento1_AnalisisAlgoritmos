from __future__ import annotations
"""Limpieza y normalizacion de series por activo.

Reglas principales:
- Parseo robusto de valores numericos.
- Eliminacion de registros invalidos.
- Imputacion de close faltante con vecinos temporales.
- Correccion de coherencia OHLC y volumen.

Secuencia aplicada en clean_asset_rows():
1) Parsear fecha y campos OHLCV.
2) Ordenar por fecha.
3) Resolver duplicados por fecha.
4) Imputar close faltante (promedio vecinos o arrastre).
5) Normalizar coherencia de precios (high/low/open/close).
6) Corregir volumen invalido a 0.
7) Retornar lista de PriceRow lista para unificacion.
"""

import datetime as dt
import math

from src.domain.models import PriceRow


def _to_float_or_none(value: str | None) -> float | None:
    """Convierte texto a float valido o retorna None si no es utilizable."""
    if value is None:
        return None
    value = value.strip()
    if value == "" or value.lower() in {"nan", "null", "none"}:
        return None
    try:
        parsed = float(value)
        if math.isfinite(parsed):
            return parsed
        return None
    except ValueError:
        return None


def _to_int_or_none(value: str | None) -> int | None:
    """Convierte texto a entero valido o retorna None."""
    if value is None:
        return None
    value = value.strip()
    if value == "" or value.lower() in {"nan", "null", "none"}:
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def clean_asset_rows(asset: str, rows: list[dict[str, str]]) -> list[PriceRow]:
    """Limpia los registros de un activo y retorna filas consistentes.

La salida esta lista para ser unificada con otros activos.

Entrada esperada:
    rows: lista de diccionarios con Date/Open/High/Low/Close/Volume.

Salida:
    lista de PriceRow coherente y util para analisis.
    """
    parsed: list[dict[str, object]] = []

    for row in rows:
        try:
            date = dt.date.fromisoformat(row["Date"])
        except Exception:
            continue

        parsed.append(
            {
                "date": date,
                "open": _to_float_or_none(row.get("Open")),
                "high": _to_float_or_none(row.get("High")),
                "low": _to_float_or_none(row.get("Low")),
                "close": _to_float_or_none(row.get("Close")),
                "volume": _to_int_or_none(row.get("Volume")),
            }
        )

    parsed.sort(key=lambda x: x["date"])

    dedup: dict[dt.date, dict[str, object]] = {}
    for item in parsed:
        # Si hay fechas duplicadas, se conserva la ultima observada.
        dedup[item["date"]] = item
    parsed = [dedup[d] for d in sorted(dedup)]

    closes = [item["close"] for item in parsed]
    n = len(parsed)

    for i in range(n):
        if closes[i] is None:
            prev_close = None
            next_close = None

            for j in range(i - 1, -1, -1):
                if closes[j] is not None:
                    prev_close = float(closes[j])
                    break

            for j in range(i + 1, n):
                if closes[j] is not None:
                    next_close = float(closes[j])
                    break

            if prev_close is not None and next_close is not None:
                closes[i] = (prev_close + next_close) / 2.0
            elif prev_close is not None:
                closes[i] = prev_close
            elif next_close is not None:
                closes[i] = next_close

    cleaned: list[PriceRow] = []

    for i, row in enumerate(parsed):
        close = closes[i]
        if close is None or close <= 0:
            # Registro no confiable para analisis posterior.
            continue

        open_value = row["open"] if row["open"] is not None and row["open"] > 0 else close
        high_value = row["high"] if row["high"] is not None and row["high"] > 0 else max(open_value, close)
        low_value = row["low"] if row["low"] is not None and row["low"] > 0 else min(open_value, close)

        if high_value < low_value:
            high_value, low_value = low_value, high_value
        if open_value < low_value:
            open_value = low_value
        if open_value > high_value:
            open_value = high_value
        if close < low_value:
            close = low_value
        if close > high_value:
            close = high_value

        volume = row["volume"] if row["volume"] is not None and row["volume"] >= 0 else 0

        cleaned.append(
            PriceRow(
                asset=asset,
                date=row["date"],
                open=float(open_value),
                high=float(high_value),
                low=float(low_value),
                close=float(close),
                volume=int(volume),
                is_imputed=0,
                source="observed",
            )
        )

    return cleaned

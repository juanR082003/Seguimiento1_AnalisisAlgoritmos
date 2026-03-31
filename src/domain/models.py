from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass
class PriceRow:
    asset: str
    date: dt.date
    open: float
    high: float
    low: float
    close: float
    volume: int
    is_imputed: int
    source: str

    def to_csv_row(self) -> list[str]:
        return [
            self.asset,
            self.date.isoformat(),
            f"{self.open:.6f}",
            f"{self.high:.6f}",
            f"{self.low:.6f}",
            f"{self.close:.6f}",
            str(self.volume),
            str(self.is_imputed),
            self.source,
        ]

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from mybroker.models import PriceBar


REQUIRED_PRICE_COLUMNS = {"date", "symbol", "close"}


def load_price_csv(path: str | Path) -> list[PriceBar]:
    source = Path(path)
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_PRICE_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
        rows = [_parse_price_row(row, source) for row in reader]
    if not rows:
        raise ValueError(f"no price rows found: {source}")
    return sorted(rows, key=lambda row: (row.symbol, row.as_of))


def _parse_price_row(row: dict[str, str], source: Path) -> PriceBar:
    symbol = row["symbol"].strip().upper()
    if not symbol:
        raise ValueError(f"blank symbol in {source}")
    close = float(row["close"])
    if close <= 0:
        raise ValueError(f"close must be positive for {symbol}")
    return PriceBar(symbol=symbol, as_of=date.fromisoformat(row["date"]), close=close)

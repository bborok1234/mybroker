from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Protocol

from mybroker.models import DataSourceMetadata, PriceBar


REQUIRED_PRICE_COLUMNS = {"date", "symbol", "close"}
DEFAULT_SAMPLE_PRICE_PATH = Path(__file__).resolve().parents[2] / "examples" / "prices.csv"


class PriceDataAdapter(Protocol):
    adapter_id: str

    def load(self) -> list[PriceBar]:
        ...

    def metadata(self, bars: list[PriceBar]) -> DataSourceMetadata:
        ...


class CsvPriceDataAdapter:
    adapter_id = "csv_price_v1"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[PriceBar]:
        return load_price_csv(self.path)

    def metadata(self, bars: list[PriceBar]) -> DataSourceMetadata:
        return price_source_metadata(self.adapter_id, str(self.path), bars)


class SamplePriceDataAdapter(CsvPriceDataAdapter):
    adapter_id = "sample_price_v1"

    def __init__(self, path: str | Path = DEFAULT_SAMPLE_PRICE_PATH) -> None:
        super().__init__(path)


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


def price_source_metadata(adapter_id: str, source: str, bars: list[PriceBar]) -> DataSourceMetadata:
    if not bars:
        raise ValueError("cannot describe an empty price source")
    return DataSourceMetadata(
        adapter_id=adapter_id,
        source=source,
        row_count=len(bars),
        symbols=sorted({bar.symbol for bar in bars}),
    )


def _parse_price_row(row: dict[str, str], source: Path) -> PriceBar:
    symbol = row["symbol"].strip().upper()
    if not symbol:
        raise ValueError(f"blank symbol in {source}")
    close = float(row["close"])
    if close <= 0:
        raise ValueError(f"close must be positive for {symbol}")
    return PriceBar(symbol=symbol, as_of=date.fromisoformat(row["date"]), close=close)

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Iterable, Protocol

from mybroker.models import DataQualityIssue, DataQualityResult, DataSourceMetadata, PriceBar, PriceDataset


REQUIRED_PRICE_COLUMNS = {"date", "symbol", "close"}
DEFAULT_SAMPLE_PRICE_PATH = Path(__file__).resolve().parents[2] / "examples" / "prices.csv"


class PriceDataAdapter(Protocol):
    adapter_id: str

    def load(self) -> list[PriceBar]:
        ...

    def load_dataset(self, min_history: int = 5) -> PriceDataset:
        ...

    def metadata(self, bars: list[PriceBar]) -> DataSourceMetadata:
        ...


class CsvPriceDataAdapter:
    adapter_id = "csv_price_v1"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[PriceBar]:
        dataset = self.load_dataset()
        _raise_on_quality_errors(dataset.quality)
        return dataset.bars

    def load_dataset(self, min_history: int = 5) -> PriceDataset:
        return load_price_dataset(self.path, adapter_id=self.adapter_id, min_history=min_history)

    def metadata(self, bars: list[PriceBar]) -> DataSourceMetadata:
        return price_source_metadata(self.adapter_id, str(self.path), bars, sources=[str(self.path)])


class MultiCsvPriceDataAdapter:
    adapter_id = "multi_csv_price_v1"

    def __init__(self, sources: Iterable[str | Path]) -> None:
        self.sources = [Path(source) for source in sources]

    def load(self) -> list[PriceBar]:
        dataset = self.load_dataset()
        _raise_on_quality_errors(dataset.quality)
        return dataset.bars

    def load_dataset(self, min_history: int = 5) -> PriceDataset:
        return load_price_dataset(self.sources, adapter_id=self.adapter_id, min_history=min_history)

    def metadata(self, bars: list[PriceBar]) -> DataSourceMetadata:
        return price_source_metadata(self.adapter_id, "multi-csv", bars, sources=[str(path) for path in self.sources])


class DirectoryPriceDataAdapter(MultiCsvPriceDataAdapter):
    adapter_id = "directory_csv_price_v1"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        super().__init__(sorted(self.path.glob("*.csv")))


class SamplePriceDataAdapter(CsvPriceDataAdapter):
    adapter_id = "sample_price_v1"

    def __init__(self, path: str | Path = DEFAULT_SAMPLE_PRICE_PATH) -> None:
        super().__init__(path)


def load_price_csv(path: str | Path) -> list[PriceBar]:
    dataset = load_price_dataset(path)
    _raise_on_quality_errors(dataset.quality)
    return dataset.bars


def load_price_dataset(source: str | Path | Iterable[str | Path], *, adapter_id: str = "csv_price_v1", min_history: int = 5) -> PriceDataset:
    files = resolve_price_files(source)
    issues: list[DataQualityIssue] = []
    bars: list[PriceBar] = []
    seen_keys: set[tuple[str, date]] = set()
    last_seen_by_symbol: dict[str, date] = {}
    if not files:
        issues.append(DataQualityIssue("error", "no_csv_files", "No CSV files found for price dataset."))
    for file_path in files:
        bars.extend(_read_price_file(file_path, issues, seen_keys, last_seen_by_symbol))
    if not bars:
        issues.append(DataQualityIssue("error", "no_valid_rows", "No valid price rows found."))
    _append_coverage_issues(bars, issues, min_history)
    sorted_bars = sorted(bars, key=lambda row: (row.symbol, row.as_of))
    quality = build_quality_result(issues)
    source_list = [path.as_posix() for path in files]
    metadata = (
        price_source_metadata(
            adapter_id=adapter_id,
            source=_source_label(files),
            bars=sorted_bars,
            sources=source_list,
            source_type="directory" if len(files) > 1 else "file",
        )
        if sorted_bars
        else DataSourceMetadata(
            adapter_id=adapter_id,
            source=_source_label(files),
            row_count=0,
            symbols=[],
            sources=source_list,
            source_type="directory" if len(files) > 1 else "file",
            file_count=len(source_list),
        )
    )
    return PriceDataset(bars=sorted_bars, metadata=metadata, quality=quality)


def resolve_price_files(source: str | Path | Iterable[str | Path]) -> list[Path]:
    if isinstance(source, str | Path):
        path = Path(source)
        if path.is_dir():
            return sorted(path.glob("*.csv"))
        return [path]
    files: list[Path] = []
    for item in source:
        path = Path(item)
        if path.is_dir():
            files.extend(sorted(path.glob("*.csv")))
        else:
            files.append(path)
    return sorted(dict.fromkeys(files))


def build_quality_result(issues: list[DataQualityIssue]) -> DataQualityResult:
    checks = {
        "schema": not any(issue.code == "missing_columns" for issue in issues),
        "missing_values": not any(issue.code == "missing_value" for issue in issues),
        "duplicates": not any(issue.code == "duplicate_row" for issue in issues),
        "date_order": not any(issue.code == "date_order" for issue in issues),
        "symbol_coverage": not any(issue.code == "symbol_coverage" for issue in issues),
        "insufficient_history": not any(issue.code == "insufficient_history" for issue in issues),
    }
    error_count = sum(1 for issue in issues if issue.level == "error")
    warning_count = sum(1 for issue in issues if issue.level == "warning")
    status = "error" if error_count else "warning" if warning_count else "pass"
    return DataQualityResult(
        status=status,
        checks=checks,
        issue_count=len(issues),
        warning_count=warning_count,
        error_count=error_count,
        issues=issues,
    )


def price_source_metadata(
    adapter_id: str,
    source: str,
    bars: list[PriceBar],
    *,
    sources: list[str] | None = None,
    source_type: str = "file",
) -> DataSourceMetadata:
    if not bars:
        raise ValueError("cannot describe an empty price source")
    dates = [bar.as_of for bar in bars]
    source_list = sources or [source]
    return DataSourceMetadata(
        adapter_id=adapter_id,
        source=source,
        row_count=len(bars),
        symbols=sorted({bar.symbol for bar in bars}),
        sources=source_list,
        source_type=source_type,
        file_count=len(source_list),
        start_date=min(dates).isoformat(),
        end_date=max(dates).isoformat(),
    )


def _read_price_file(
    source: Path,
    issues: list[DataQualityIssue],
    seen_keys: set[tuple[str, date]],
    last_seen_by_symbol: dict[str, date],
) -> list[PriceBar]:
    rows: list[PriceBar] = []
    if not source.exists():
        issues.append(DataQualityIssue("error", "missing_file", f"Price file does not exist: {source}", source.as_posix()))
        return rows
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_PRICE_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            issues.append(DataQualityIssue("error", "missing_columns", f"Missing required columns: {', '.join(sorted(missing))}", source.as_posix()))
            return rows
        for line_number, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items()}
            if any(not row.get(column) for column in REQUIRED_PRICE_COLUMNS):
                issues.append(DataQualityIssue("error", "missing_value", f"Missing required value on line {line_number}.", source.as_posix()))
                continue
            parsed = _parse_price_row(row, source, line_number, issues)
            if parsed is None:
                continue
            key = (parsed.symbol, parsed.as_of)
            if key in seen_keys:
                issues.append(DataQualityIssue("warning", "duplicate_row", f"Duplicate price row for {parsed.symbol} on {parsed.as_of}.", source.as_posix(), parsed.symbol))
                continue
            last_seen = last_seen_by_symbol.get(parsed.symbol)
            if last_seen and parsed.as_of < last_seen:
                issues.append(DataQualityIssue("warning", "date_order", f"Rows for {parsed.symbol} are not ordered by date.", source.as_posix(), parsed.symbol))
            last_seen_by_symbol[parsed.symbol] = parsed.as_of
            seen_keys.add(key)
            rows.append(parsed)
    return rows


def _parse_price_row(row: dict[str, str], source: Path, line_number: int, issues: list[DataQualityIssue]) -> PriceBar | None:
    symbol = row["symbol"].strip().upper()
    if not symbol:
        issues.append(DataQualityIssue("error", "missing_value", f"Blank symbol on line {line_number}.", source.as_posix()))
        return None
    try:
        close = float(row["close"])
    except ValueError:
        issues.append(DataQualityIssue("error", "invalid_close", f"Invalid close for {symbol} on line {line_number}.", source.as_posix(), symbol))
        return None
    if close <= 0:
        issues.append(DataQualityIssue("error", "invalid_close", f"Close must be positive for {symbol} on line {line_number}.", source.as_posix(), symbol))
        return None
    try:
        as_of = date.fromisoformat(row["date"])
    except ValueError:
        issues.append(DataQualityIssue("error", "invalid_date", f"Invalid date for {symbol} on line {line_number}.", source.as_posix(), symbol))
        return None
    return PriceBar(symbol=symbol, as_of=as_of, close=close)


def _append_coverage_issues(bars: list[PriceBar], issues: list[DataQualityIssue], min_history: int) -> None:
    counts = Counter(bar.symbol for bar in bars)
    if not counts:
        issues.append(DataQualityIssue("error", "symbol_coverage", "No symbols found in dataset."))
        return
    for symbol, count in sorted(counts.items()):
        if count < min_history:
            issues.append(DataQualityIssue("warning", "insufficient_history", f"{symbol} has {count} rows; need {min_history}.", symbol=symbol))


def _source_label(files: list[Path]) -> str:
    if len(files) == 1:
        return files[0].as_posix()
    parents = {path.parent.as_posix() for path in files}
    if len(parents) == 1:
        return sorted(parents)[0]
    return "multi-csv"


def _raise_on_quality_errors(quality: DataQualityResult) -> None:
    if quality.error_count:
        messages = "; ".join(issue.message for issue in quality.issues if issue.level == "error")
        raise ValueError(f"price dataset has blocking quality errors: {messages}")

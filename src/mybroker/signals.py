from __future__ import annotations

from collections import defaultdict

from mybroker.models import PriceBar, Signal


def momentum_signals(bars: list[PriceBar], short_window: int = 3, long_window: int = 5) -> list[Signal]:
    if short_window <= 0 or long_window <= 0:
        raise ValueError("window sizes must be positive")
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window")

    by_symbol: dict[str, list[PriceBar]] = defaultdict(list)
    for bar in bars:
        by_symbol[bar.symbol].append(bar)

    signals = []
    for symbol, rows in sorted(by_symbol.items()):
        rows = sorted(rows, key=lambda row: row.as_of)
        if len(rows) < long_window:
            last = rows[-1]
            signals.append(
                Signal(
                    symbol=symbol,
                    as_of=last.as_of,
                    name="momentum",
                    score=0.0,
                    direction="insufficient_data",
                    confidence=0.0,
                    rationale=f"Need {long_window} observations, found {len(rows)}.",
                    evidence=[f"observations={len(rows)}"],
                )
            )
            continue

        recent = rows[-short_window:]
        baseline = rows[-long_window:]
        short_avg = _average_close(recent)
        long_avg = _average_close(baseline)
        score = (short_avg - long_avg) / long_avg
        direction = _direction(score)
        confidence = min(abs(score) * 10.0, 1.0)
        last = rows[-1]
        signals.append(
            Signal(
                symbol=symbol,
                as_of=last.as_of,
                name="momentum",
                score=round(score, 6),
                direction=direction,
                confidence=round(confidence, 4),
                rationale=(
                    f"{short_window}-period average {short_avg:.4f} versus "
                    f"{long_window}-period average {long_avg:.4f}."
                ),
                evidence=[
                    f"short_window={short_window}",
                    f"long_window={long_window}",
                    f"last_close={last.close}",
                ],
            )
        )
    return signals


def _average_close(rows: list[PriceBar]) -> float:
    return sum(row.close for row in rows) / len(rows)


def _direction(score: float) -> str:
    if score > 0.01:
        return "positive_watch"
    if score < -0.01:
        return "negative_watch"
    return "neutral_watch"

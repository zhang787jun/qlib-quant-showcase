from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import numpy as np
import pandas as pd


DEFAULT_SYMBOLS = ("SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "GLD", "DBC")


@dataclass(frozen=True)
class PricePanel:
    prices: pd.DataFrame
    source: str


def generate_sample_prices(
    symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
    start: str = "2015-01-01",
    end: str = "2025-12-31",
    seed: int = 42,
) -> PricePanel:
    """Generate deterministic public-safe sample prices.

    The sample is synthetic by design: it makes the repository runnable in CI
    without carrying private portfolio data or requiring a paid market-data key.
    """

    dates = pd.bdate_range(start=start, end=end)
    rng = np.random.default_rng(seed)

    market = rng.normal(0.00025, 0.008, size=len(dates))
    rates = rng.normal(0.00005, 0.004, size=len(dates))
    commodity = rng.normal(0.00012, 0.010, size=len(dates))

    exposures = {
        "SPY": (1.00, -0.15, 0.05, 0.006),
        "QQQ": (1.18, -0.25, 0.02, 0.009),
        "IWM": (1.28, -0.10, 0.04, 0.011),
        "EFA": (0.88, -0.05, 0.08, 0.008),
        "EEM": (1.08, 0.00, 0.12, 0.012),
        "TLT": (-0.20, 1.00, 0.00, 0.007),
        "GLD": (0.10, 0.25, 0.40, 0.009),
        "DBC": (0.25, -0.05, 1.00, 0.012),
    }

    log_returns: dict[str, np.ndarray] = {}
    for symbol in symbols:
        beta_m, beta_r, beta_c, idio_vol = exposures.get(symbol, (0.9, 0.0, 0.1, 0.01))
        drift = 0.00008 + 0.00003 * (symbols.index(symbol) % 3)
        idio = rng.normal(0.0, idio_vol, size=len(dates))
        log_returns[symbol] = drift + beta_m * market + beta_r * rates + beta_c * commodity + idio

    prices = pd.DataFrame(log_returns, index=dates).cumsum().pipe(np.exp) * 100.0
    prices.index.name = "date"
    return PricePanel(prices=prices.round(4), source="deterministic synthetic sample")


def fetch_stooq_prices(
    symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
    start: str = "2015-01-01",
    end: str = "2025-12-31",
    timeout: float = 10.0,
) -> PricePanel:
    """Fetch adjusted daily closes from Stooq's public CSV endpoint.

    This is optional for local exploration. The scripts fall back to
    deterministic sample data when a network call fails.
    """

    start_key = start.replace("-", "")
    end_key = end.replace("-", "")
    frames: list[pd.Series] = []
    for symbol in symbols:
        stooq_symbol = f"{symbol.lower()}.us"
        url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&d1={start_key}&d2={end_key}&i=d"
        try:
            with urlopen(url, timeout=timeout) as response:
                frame = pd.read_csv(response)
        except (OSError, URLError) as exc:
            raise RuntimeError(f"failed to fetch {symbol} from Stooq") from exc

        if frame.empty or "Close" not in frame.columns:
            raise RuntimeError(f"Stooq returned no close prices for {symbol}")
        series = pd.Series(frame["Close"].to_numpy(), index=pd.to_datetime(frame["Date"]), name=symbol)
        frames.append(series)

    prices = pd.concat(frames, axis=1).sort_index().ffill().dropna(how="all")
    prices.index.name = "date"
    return PricePanel(prices=prices, source="Stooq public daily close")


def load_prices(
    source: str = "sample",
    symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
    start: str = "2015-01-01",
    end: str = "2025-12-31",
) -> PricePanel:
    if source == "sample":
        return generate_sample_prices(symbols=symbols, start=start, end=end)
    if source == "stooq":
        try:
            return fetch_stooq_prices(symbols=symbols, start=start, end=end)
        except RuntimeError:
            return generate_sample_prices(symbols=symbols, start=start, end=end)
    raise ValueError(f"unsupported source: {source}")


def write_prices(prices: pd.DataFrame, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(target, index_label="date")


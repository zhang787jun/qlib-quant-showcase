from __future__ import annotations

import numpy as np
import pandas as pd


def trailing_return(prices: pd.DataFrame, lookback: int) -> pd.DataFrame:
    return prices.pct_change(lookback)


def realized_volatility(prices: pd.DataFrame, lookback: int = 63) -> pd.DataFrame:
    return prices.pct_change().rolling(lookback).std() * np.sqrt(252)


def trend_strength(prices: pd.DataFrame, short: int = 63, long: int = 252) -> pd.DataFrame:
    return prices.rolling(short).mean() / prices.rolling(long).mean() - 1.0


def forward_returns(prices: pd.DataFrame, horizon: int = 21) -> pd.DataFrame:
    return prices.shift(-horizon) / prices - 1.0


def build_factor_frame(prices: pd.DataFrame, horizon: int = 21) -> pd.DataFrame:
    """Build a date-symbol factor table.

    All factors at date t use information available at or before t. The target
    is the next `horizon` business-day return from t to t+horizon.
    """

    factor_map = {
        "momentum_126": trailing_return(prices, 126),
        "momentum_252": trailing_return(prices, 252),
        "reversal_21": -trailing_return(prices, 21),
        "low_vol_63": -realized_volatility(prices, 63),
        "trend_strength": trend_strength(prices, 63, 252),
        "forward_return_21": forward_returns(prices, horizon),
    }

    stacked = []
    for name, frame in factor_map.items():
        stacked.append(frame.stack().rename(name))
    result = pd.concat(stacked, axis=1)
    result.index.names = ["date", "symbol"]
    return result.dropna()


def zscore_by_date(values: pd.Series) -> pd.Series:
    grouped = values.groupby(level="date")
    means = grouped.transform("mean")
    stds = grouped.transform("std").replace(0.0, np.nan)
    return (values - means) / stds


def composite_alpha(factors: pd.DataFrame) -> pd.Series:
    components = [
        zscore_by_date(factors["momentum_126"]),
        zscore_by_date(factors["momentum_252"]),
        zscore_by_date(factors["low_vol_63"]),
        zscore_by_date(factors["trend_strength"]),
        0.5 * zscore_by_date(factors["reversal_21"]),
    ]
    alpha = pd.concat(components, axis=1).mean(axis=1)
    alpha.name = "composite_alpha"
    return alpha

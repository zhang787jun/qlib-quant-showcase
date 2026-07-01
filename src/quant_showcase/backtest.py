from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .metrics import markdown_table, performance_summary, to_percent


def month_end_rebalance_dates(prices: pd.DataFrame) -> pd.DatetimeIndex:
    return prices.resample("ME").last().index.intersection(prices.index)


def dual_momentum_weights(
    prices: pd.DataFrame,
    lookback: int = 126,
    top_n: int = 3,
    rebalance: str = "ME",
) -> pd.DataFrame:
    if rebalance != "ME":
        raise ValueError("only month-end rebalancing is supported in v0.1")

    returns = prices.pct_change(lookback)
    rebalance_dates = month_end_rebalance_dates(prices)
    rebalance_weights = pd.DataFrame(0.0, index=rebalance_dates, columns=prices.columns)

    for date in rebalance_dates:
        if date not in returns.index:
            continue
        signal = returns.loc[date].dropna()
        signal = signal[signal > 0].sort_values(ascending=False).head(top_n)
        if signal.empty:
            continue
        rebalance_weights.loc[date, signal.index] = 1.0 / len(signal)

    return rebalance_weights.reindex(prices.index).ffill().fillna(0.0)


def run_backtest(prices: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    asset_returns = prices.pct_change().fillna(0.0)
    aligned_weights = weights.reindex(asset_returns.index).ffill().fillna(0.0)
    strategy_returns = (aligned_weights.shift(1).fillna(0.0) * asset_returns).sum(axis=1)
    benchmark_returns = asset_returns.mean(axis=1)
    result = pd.DataFrame(
        {
            "strategy_return": strategy_returns,
            "benchmark_return": benchmark_returns,
            "strategy_equity": (1.0 + strategy_returns).cumprod(),
            "benchmark_equity": (1.0 + benchmark_returns).cumprod(),
        }
    )
    result.index.name = "date"
    return result


def turnover(weights: pd.DataFrame) -> float:
    diffs = weights.diff().abs().sum(axis=1)
    active = diffs[diffs > 0]
    if active.empty:
        return 0.0
    return float(active.mean())


def run_strategy_backtest(prices: pd.DataFrame, output_dir: str | Path) -> dict[str, pd.DataFrame]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    weights = dual_momentum_weights(prices)
    backtest = run_backtest(prices, weights)
    strategy_metrics = performance_summary(backtest["strategy_return"])
    benchmark_metrics = performance_summary(backtest["benchmark_return"])

    metrics = pd.DataFrame(
        [
            {"portfolio": "dual_momentum", **strategy_metrics, "avg_rebalance_turnover": turnover(weights)},
            {"portfolio": "equal_weight_benchmark", **benchmark_metrics, "avg_rebalance_turnover": 0.0},
        ]
    )

    weights.to_csv(output / "strategy_weights.csv")
    backtest.to_csv(output / "equity_curve.csv")
    metrics.to_csv(output / "performance_summary.csv", index=False)
    write_backtest_report(output / "strategy_backtest_report.md", metrics)
    return {"weights": weights, "backtest": backtest, "metrics": metrics}


def write_backtest_report(path: str | Path, metrics: pd.DataFrame) -> None:
    strategy = metrics.loc[metrics["portfolio"] == "dual_momentum"].iloc[0]
    benchmark = metrics.loc[metrics["portfolio"] == "equal_weight_benchmark"].iloc[0]
    lines = [
        "# Strategy Backtest Report",
        "",
        "## Executive summary",
        "",
        f"- Strategy CAGR: `{to_percent(strategy['cagr'])}` vs benchmark `{to_percent(benchmark['cagr'])}`.",
        f"- Strategy Sharpe: `{strategy['sharpe']:.2f}` vs benchmark `{benchmark['sharpe']:.2f}`.",
        f"- Strategy max drawdown: `{to_percent(strategy['max_drawdown'])}` vs benchmark `{to_percent(benchmark['max_drawdown'])}`.",
        "",
        "## Performance summary",
        "",
        markdown_table(metrics),
        "",
        "## Strategy definition",
        "",
        "- Universe: default ETF-style public sample universe.",
        "- Signal: 126-business-day absolute and cross-sectional momentum.",
        "- Rebalance: month end.",
        "- Allocation: equal weight top 3 assets with positive momentum; cash if no positive momentum.",
        "- Costs: not modeled in v0.1; add explicit cost assumptions before using with real capital.",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")

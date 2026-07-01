from __future__ import annotations

from quant_showcase.backtest import dual_momentum_weights, run_strategy_backtest
from quant_showcase.data import generate_sample_prices


def test_dual_momentum_weights_are_valid() -> None:
    prices = generate_sample_prices(end="2018-12-31").prices
    weights = dual_momentum_weights(prices)

    assert weights.index.equals(prices.index)
    assert set(weights.columns) == set(prices.columns)
    assert (weights.sum(axis=1) <= 1.0000001).all()
    assert (weights >= 0).all().all()


def test_strategy_backtest_writes_public_artifacts(tmp_path) -> None:
    prices = generate_sample_prices(end="2019-12-31").prices
    result = run_strategy_backtest(prices, tmp_path)

    assert not result["backtest"].empty
    assert {"strategy_return", "benchmark_return", "strategy_equity", "benchmark_equity"}.issubset(
        result["backtest"].columns
    )
    assert not result["metrics"].empty
    assert (tmp_path / "performance_summary.csv").exists()
    assert (tmp_path / "equity_curve.csv").exists()
    assert (tmp_path / "strategy_backtest_report.md").exists()


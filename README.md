# Qlib Quant Showcase

[![Tests](https://github.com/zhang787jun/qlib-quant-showcase/actions/workflows/tests.yml/badge.svg)](https://github.com/zhang787jun/qlib-quant-showcase/actions/workflows/tests.yml)

Two public, reproducible quant projects:

1. **Cross-sectional factor research**: momentum, reversal, low-volatility, and trend-strength factors with IC and quantile-return diagnostics.
2. **Dual-momentum strategy backtest**: month-end allocation to the top positive-momentum assets versus an equal-weight benchmark.

The repository is intentionally public-safe: default runs use deterministic synthetic ETF-style prices, so the examples do not expose private holdings or require paid market data. Optional Stooq public-price fetching is available for local exploration.

## Quickstart

```bash
git clone https://github.com/zhang787jun/qlib-quant-showcase.git
cd qlib-quant-showcase
python3 -m pip install -e ".[dev]"
python3 scripts/run_factor_research.py --source sample
python3 scripts/run_strategy_backtest.py --source sample
pytest -q
```

Generated artifacts:

```text
results/
├── factor_research/
│   ├── factor_observations.csv
│   ├── factor_ic_summary.csv
│   ├── factor_research_report.md
│   ├── prices.csv
│   └── quantile_return_summary.csv
└── strategy_backtest/
    ├── equity_curve.csv
    ├── performance_summary.csv
    ├── prices.csv
    ├── strategy_backtest_report.md
    └── strategy_weights.csv
```

## Project 1: Factor Research

Research question:

> Do simple cross-sectional factors contain useful forward-return signal in a diversified ETF-style universe?

Implemented factors:

- `momentum_126`: 126-business-day total return.
- `momentum_252`: 252-business-day total return.
- `reversal_21`: negative 21-business-day return.
- `low_vol_63`: negative realized 63-business-day volatility.
- `trend_strength`: 63-day moving average versus 252-day moving average.
- `composite_alpha`: average cross-sectional z-score of the above signals.

Outputs:

- Information coefficient summary.
- Forward 21-day return by factor quantile.
- Markdown report for GitHub review.

Run:

```bash
python3 scripts/run_factor_research.py --source sample
```

## Project 2: Strategy Backtest

Research question:

> Can a simple absolute and cross-sectional momentum rule improve risk-adjusted returns versus an equal-weight benchmark?

Rules:

- Universe: default ETF-style sample universe.
- Signal: 126-business-day momentum.
- Rebalance: month end.
- Allocation: equal weight the top 3 assets with positive momentum.
- Risk-off behavior: hold cash when no asset has positive momentum.

Outputs:

- Daily strategy and benchmark equity curve.
- Monthly strategy weights.
- Performance summary with CAGR, volatility, Sharpe, max drawdown, Calmar, hit rate, and average rebalance turnover.
- Markdown report for GitHub review.

Run:

```bash
python3 scripts/run_strategy_backtest.py --source sample
```

## Optional Public Data

To try public Stooq daily closes:

```bash
python3 scripts/run_factor_research.py --source stooq
python3 scripts/run_strategy_backtest.py --source stooq
```

If the network call fails, the loader falls back to deterministic sample data so tests and demos still run.

## Repository Layout

```text
docs/project-spec.md              # public project scope and non-goals
scripts/run_factor_research.py    # factor research entrypoint
scripts/run_strategy_backtest.py  # strategy backtest entrypoint
src/quant_showcase/               # reusable quant code
tests/                            # pytest coverage
results/                          # generated reports and CSV artifacts
```

## Roadmap

- Add transaction-cost and slippage assumptions.
- Add walk-forward parameter checks.
- Add Qlib data-handler integration after the public minimum projects are stable.
- Extend GitHub Actions to regenerate sample reports on demand.

## Risk Notice

This repository is for research and engineering demonstration only. It is not investment advice, does not model all transaction costs or taxes, and should not be used for live trading without independent validation.

# Strategy Backtest Report

## Executive summary

- Strategy CAGR: `13.12%` vs benchmark `9.87%`.
- Strategy Sharpe: `0.98` vs benchmark `0.90`.
- Strategy max drawdown: `-22.70%` vs benchmark `-30.66%`.

## Performance summary

| portfolio | cagr | annualized_volatility | sharpe | max_drawdown | calmar | hit_rate | avg_rebalance_turnover |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dual_momentum | 0.1312 | 0.1343 | 0.9772 | -0.2270 | 0.5779 | 0.4962 | 0.8485 |
| equal_weight_benchmark | 0.0987 | 0.1094 | 0.9020 | -0.3066 | 0.3218 | 0.5244 | 0.0000 |

## Strategy definition

- Universe: default ETF-style public sample universe.
- Signal: 126-business-day absolute and cross-sectional momentum.
- Rebalance: month end.
- Allocation: equal weight top 3 assets with positive momentum; cash if no positive momentum.
- Costs: not modeled in v0.1; add explicit cost assumptions before using with real capital.

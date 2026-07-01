# Factor Research Report

## Executive summary

- Best standalone factor by mean IC: `trend_strength`.
- Mean IC: `0.0589`; IC IR: `0.14`.
- Top-minus-bottom 21-day quantile return spread: `0.5345%`.

## IC summary

| factor | mean_ic | ic_vol | ic_ir | positive_ic_rate | observations |
| --- | --- | --- | --- | --- | --- |
| trend_strength | 0.0589 | 0.4336 | 0.1358 | 0.5522 | 2597 |
| composite_alpha | 0.0547 | 0.4336 | 0.1261 | 0.5422 | 2597 |
| momentum_126 | 0.0446 | 0.4286 | 0.1041 | 0.5456 | 2597 |
| momentum_252 | 0.0388 | 0.4375 | 0.0887 | 0.5256 | 2597 |
| low_vol_63 | 0.0010 | 0.4183 | 0.0025 | 0.4913 | 2597 |
| reversal_21 | -0.0245 | 0.3974 | -0.0617 | 0.4740 | 2597 |

## Quantile return summary

| quantile | mean_forward_return | forward_return_vol | count | annualized_mean_proxy |
| --- | --- | --- | --- | --- |
| 1.0000 | 0.0084 | 0.0658 | 5194.0000 | 0.1057 |
| 2.0000 | 0.0034 | 0.0595 | 5194.0000 | 0.0421 |
| 3.0000 | 0.0056 | 0.0555 | 5194.0000 | 0.0695 |
| 4.0000 | 0.0138 | 0.0526 | 5194.0000 | 0.1782 |

## Notes

- Factor values at date t use information available at or before t.
- The forward return target is the next 21 business-day return.
- The default dataset is deterministic synthetic sample data for CI safety.

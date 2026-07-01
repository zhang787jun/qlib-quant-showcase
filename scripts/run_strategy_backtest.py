#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from quant_showcase.backtest import run_strategy_backtest
from quant_showcase.data import load_prices, write_prices


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public strategy backtest project.")
    parser.add_argument("--source", choices=["sample", "stooq"], default="sample")
    parser.add_argument("--output", default="results/strategy_backtest")
    args = parser.parse_args()

    panel = load_prices(source=args.source)
    output = Path(args.output)
    write_prices(panel.prices, output / "prices.csv")
    run_strategy_backtest(panel.prices, output)
    print(f"strategy backtest complete: {output} ({panel.source})")


if __name__ == "__main__":
    main()


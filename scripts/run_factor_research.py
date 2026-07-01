#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from quant_showcase.data import load_prices, write_prices
from quant_showcase.factor_research import run_factor_research


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public factor research project.")
    parser.add_argument("--source", choices=["sample", "stooq"], default="sample")
    parser.add_argument("--output", default="results/factor_research")
    args = parser.parse_args()

    panel = load_prices(source=args.source)
    output = Path(args.output)
    write_prices(panel.prices, output / "prices.csv")
    run_factor_research(panel.prices, output)
    print(f"factor research complete: {output} ({panel.source})")


if __name__ == "__main__":
    main()


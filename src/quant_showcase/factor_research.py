from __future__ import annotations

from pathlib import Path

import pandas as pd

from .factors import build_factor_frame, composite_alpha
from .metrics import markdown_table


def _spearman_by_date(frame: pd.DataFrame, factor: str, target: str) -> pd.Series:
    def corr(group: pd.DataFrame) -> float:
        if group[factor].nunique() < 2 or group[target].nunique() < 2:
            return float("nan")
        return float(group[factor].rank().corr(group[target].rank()))

    return frame.groupby(level="date").apply(corr).dropna()


def factor_ic_summary(factors: pd.DataFrame, target: str = "forward_return_21") -> pd.DataFrame:
    candidate_cols = [c for c in factors.columns if c != target]
    rows = []
    for column in candidate_cols:
        ic = _spearman_by_date(factors, column, target)
        rows.append(
            {
                "factor": column,
                "mean_ic": ic.mean(),
                "ic_vol": ic.std(ddof=0),
                "ic_ir": ic.mean() / ic.std(ddof=0) if ic.std(ddof=0) else 0.0,
                "positive_ic_rate": (ic > 0).mean(),
                "observations": int(ic.count()),
            }
        )
    return pd.DataFrame(rows).sort_values("mean_ic", ascending=False).reset_index(drop=True)


def quantile_return_summary(
    factors: pd.DataFrame,
    factor: str = "composite_alpha",
    target: str = "forward_return_21",
    quantiles: int = 4,
) -> pd.DataFrame:
    working = factors[[factor, target]].dropna().copy()

    def assign_quantile(group: pd.DataFrame) -> pd.Series:
        ranks = group[factor].rank(method="first")
        return pd.qcut(ranks, q=quantiles, labels=False, duplicates="drop") + 1

    working["quantile"] = working.groupby(level="date", group_keys=False).apply(assign_quantile)
    summary = (
        working.groupby("quantile")[target]
        .agg(["mean", "std", "count"])
        .rename(columns={"mean": "mean_forward_return", "std": "forward_return_vol"})
    )
    summary["annualized_mean_proxy"] = (1.0 + summary["mean_forward_return"]) ** (252 / 21) - 1.0
    return summary.reset_index()


def run_factor_research(prices: pd.DataFrame, output_dir: str | Path) -> dict[str, pd.DataFrame]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    factors = build_factor_frame(prices)
    factors["composite_alpha"] = composite_alpha(factors)

    ic = factor_ic_summary(factors)
    quantiles = quantile_return_summary(factors)

    factors.to_csv(output / "factor_observations.csv")
    ic.to_csv(output / "factor_ic_summary.csv", index=False)
    quantiles.to_csv(output / "quantile_return_summary.csv", index=False)
    write_factor_report(output / "factor_research_report.md", ic, quantiles)
    return {"factors": factors, "ic": ic, "quantiles": quantiles}


def write_factor_report(path: str | Path, ic: pd.DataFrame, quantiles: pd.DataFrame) -> None:
    top = ic.iloc[0]
    long_short = quantiles.iloc[-1]["mean_forward_return"] - quantiles.iloc[0]["mean_forward_return"]
    lines = [
        "# Factor Research Report",
        "",
        "## Executive summary",
        "",
        f"- Best standalone factor by mean IC: `{top['factor']}`.",
        f"- Mean IC: `{top['mean_ic']:.4f}`; IC IR: `{top['ic_ir']:.2f}`.",
        f"- Top-minus-bottom 21-day quantile return spread: `{long_short:.4%}`.",
        "",
        "## IC summary",
        "",
        markdown_table(ic),
        "",
        "## Quantile return summary",
        "",
        markdown_table(quantiles),
        "",
        "## Notes",
        "",
        "- Factor values at date t use information available at or before t.",
        "- The forward return target is the next 21 business-day return.",
        "- The default dataset is deterministic synthetic sample data for CI safety.",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")

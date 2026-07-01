from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def max_drawdown(equity: pd.Series) -> float:
    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    return float(drawdown.min())


def annualized_return(returns: pd.Series) -> float:
    returns = returns.dropna()
    if returns.empty:
        return 0.0
    total = float((1.0 + returns).prod())
    years = len(returns) / TRADING_DAYS
    if years <= 0:
        return 0.0
    return total ** (1.0 / years) - 1.0


def annualized_volatility(returns: pd.Series) -> float:
    returns = returns.dropna()
    if returns.empty:
        return 0.0
    return float(returns.std(ddof=0) * np.sqrt(TRADING_DAYS))


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    excess = returns.dropna() - risk_free_rate / TRADING_DAYS
    vol = annualized_volatility(excess)
    if vol == 0.0:
        return 0.0
    return annualized_return(excess) / vol


def performance_summary(returns: pd.Series) -> dict[str, float]:
    clean = returns.dropna()
    equity = (1.0 + clean).cumprod()
    cagr = annualized_return(clean)
    vol = annualized_volatility(clean)
    mdd = max_drawdown(equity) if not equity.empty else 0.0
    return {
        "cagr": cagr,
        "annualized_volatility": vol,
        "sharpe": sharpe_ratio(clean),
        "max_drawdown": mdd,
        "calmar": cagr / abs(mdd) if mdd < 0 else 0.0,
        "hit_rate": float((clean > 0).mean()) if not clean.empty else 0.0,
    }


def to_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _format_markdown_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a compact markdown table without requiring optional tabulate."""

    columns = [str(column) for column in frame.columns]
    rows = []
    for _, row in frame.iterrows():
        rows.append([_format_markdown_cell(row[column]) for column in frame.columns])

    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])

from __future__ import annotations

from quant_showcase.data import generate_sample_prices
from quant_showcase.factor_research import run_factor_research
from quant_showcase.factors import build_factor_frame, composite_alpha


def test_factor_frame_has_forward_returns_without_private_data() -> None:
    prices = generate_sample_prices(end="2017-12-31").prices
    factors = build_factor_frame(prices)
    factors["composite_alpha"] = composite_alpha(factors)

    assert "forward_return_21" in factors.columns
    assert "composite_alpha" in factors.columns
    assert factors.index.names == ["date", "symbol"]
    assert factors["composite_alpha"].notna().all()


def test_factor_research_writes_public_artifacts(tmp_path) -> None:
    prices = generate_sample_prices(end="2018-12-31").prices
    result = run_factor_research(prices, tmp_path)

    assert not result["ic"].empty
    assert not result["quantiles"].empty
    assert (tmp_path / "factor_ic_summary.csv").exists()
    assert (tmp_path / "quantile_return_summary.csv").exists()
    assert (tmp_path / "factor_research_report.md").exists()


import math

from sovereign_debt_xl.credit_risk import (
    cds_implied_default_prob,
    merton_sovereign_default_prob,
    spread_decomposition,
    zscore_sovereign,
)


def test_merton_returns_table():
    table = merton_sovereign_default_prob(80.0, 100.0, 0.20, 0.05, 1.0)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    assert "d2_distance_to_default" in metrics
    assert "default_probability" in metrics


def test_merton_deep_in_money_low_prob():
    # Assets >> Debt → very low default probability
    table = merton_sovereign_default_prob(10.0, 1000.0, 0.10, 0.02, 1.0)
    dp = [r[1] for r in table if r[0] == "default_probability"][0]
    assert dp < 0.01


def test_merton_bad_inputs():
    result = merton_sovereign_default_prob(-1.0, 100.0, 0.20, 0.05, 1.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_cds_hazard_rate():
    # 200 bps spread, 40 % recovery → hazard = 0.02 / 0.60 ≈ 0.0333
    table = cds_implied_default_prob(200.0, 0.40, 5.0)
    hz = [r[1] for r in table if r[0] == "hazard_rate"][0]
    assert abs(hz - 0.02 / 0.60) < 1e-6


def test_cds_cumulative_pd_positive():
    table = cds_implied_default_prob(150.0, 0.40, 3.0)
    cum = [r[1] for r in table if r[0] == "cumulative_pd"][0]
    assert 0.0 < cum < 1.0


def test_cds_bad_recovery():
    result = cds_implied_default_prob(200.0, 1.0, 5.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_zscore_sovereign_structure():
    table = zscore_sovereign(-0.04, 3.0, 0.80, 0.01, 0.10)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    assert "composite_zscore" in metrics
    assert "percentile_rank" in metrics


def test_zscore_sovereign_high_risk_higher_score():
    # Stressed indicators should produce a higher composite z than healthy ones
    stressed = zscore_sovereign(-0.10, 1.0, 1.20, -0.02, 0.30)
    healthy = zscore_sovereign(0.02, 8.0, 0.30, 0.05, 0.02)
    stressed_z = [r[1] for r in stressed if r[0] == "composite_zscore"][0]
    healthy_z = [r[1] for r in healthy if r[0] == "composite_zscore"][0]
    assert stressed_z > healthy_z


def test_spread_decomposition_returns_r2():
    import numpy as np

    rng = np.random.default_rng(0)
    n = 20
    vix = rng.normal(20, 5, n).tolist()
    usy = rng.normal(3, 0.5, n).tolist()
    comm = rng.normal(100, 10, n).tolist()
    fund = rng.normal(0, 1, n).tolist()
    spread = [0.5 * v + 10 * f + rng.normal(0, 5) for v, f in zip(vix, fund)]
    table = spread_decomposition(spread, vix, usy, comm, fund)
    assert any(r[0] == "R2" for r in table)
    assert any(r[0] == "global_share" for r in table)

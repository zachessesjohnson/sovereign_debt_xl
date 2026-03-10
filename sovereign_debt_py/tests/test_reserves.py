from sovereign_debt_py.reserves import (
    bop_financing_gap,
    exchange_rate_misalignment,
    reserves_adequacy_metrics,
)


def test_reserves_adequacy_import_cover():
    # 120 USD reserves, 10 USD/month imports → 12 months cover
    table = reserves_adequacy_metrics(120.0, 50.0, 10.0, 200.0, 500.0)
    assert table[0] == ["metric", "value"]
    ic = [r[1] for r in table if r[0] == "import_cover_months"][0]
    assert abs(ic - 12.0) < 1e-6


def test_reserves_adequacy_greenspan():
    # 100 reserves, 80 short-term debt → GG = 1.25
    table = reserves_adequacy_metrics(100.0, 80.0, 5.0, 300.0, 1000.0)
    gg = [r[1] for r in table if r[0] == "greenspan_guidotti"][0]
    assert abs(gg - 100.0 / 80.0) < 1e-6


def test_reserves_adequacy_negative_reserves():
    result = reserves_adequacy_metrics(-10.0, 50.0, 5.0, 100.0, 300.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_reserves_adequacy_all_metrics_present():
    table = reserves_adequacy_metrics(200.0, 100.0, 10.0, 400.0, 1000.0)
    metrics = [r[0] for r in table[1:]]
    for m in ["import_cover_months", "greenspan_guidotti", "wijnholds_kapteyn", "imf_ara_composite"]:
        assert m in metrics


def test_bop_financing_gap_zero():
    # Inflows exactly cover outflows → gap = 0
    result = bop_financing_gap(-20.0, 10.0, 10.0, 0.0, 0.0)
    assert abs(result) < 1e-9


def test_bop_financing_gap_positive():
    # Large amortization with small inflows → positive gap
    result = bop_financing_gap(-5.0, 5.0, 0.0, 30.0, 0.0)
    assert result > 0


def test_exchange_rate_misalignment_structure():
    import numpy as np

    rng = np.random.default_rng(1)
    n = 15
    tot = rng.normal(100, 5, n).tolist()
    nfa = rng.normal(-0.1, 0.05, n).tolist()
    reer_h = [1.0 * t - 0.5 * n_ + rng.normal(0, 2) for t, n_ in zip(tot, nfa)]
    table = exchange_rate_misalignment(102.0, reer_h, tot, nfa)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    for m in ["reer_observed", "reer_equilibrium", "misalignment", "misalignment_pct", "R2"]:
        assert m in metrics


def test_exchange_rate_misalignment_too_few_obs():
    result = exchange_rate_misalignment(100.0, [100.0, 101.0], [100.0, 102.0], [-0.1, -0.2])
    assert isinstance(result, str) and result.startswith("#ERR:")

from sovereign_debt_xl.stress import (
    contingent_liability_shock,
    exchange_rate_passthrough_to_debt,
    fan_chart_debt,
)


def test_fan_chart_debt_shape():
    bp = [0.03, 0.05, 0.02, 0.60]  # g, r, pb, d0
    sd = [0.01, 0.01, 0.005]
    table = fan_chart_debt(bp, sd, 200, 5)
    assert table[0] == ["year", "p10", "p25", "p50", "p75", "p90"]
    assert len(table) == 6  # header + 5 years


def test_fan_chart_debt_percentile_order():
    bp = [0.03, 0.05, 0.02, 0.60]
    sd = [0.02, 0.02, 0.01]
    table = fan_chart_debt(bp, sd, 500, 3)
    for row in table[1:]:
        _, p10, p25, p50, p75, p90 = row
        assert p10 <= p25 <= p50 <= p75 <= p90


def test_fan_chart_debt_bad_params():
    result = fan_chart_debt([0.03, 0.05], [0.01, 0.01, 0.005], 100, 3)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_contingent_liability_shock_total():
    # banking shock = 0.8 * 0.1 = 0.08, SOE shock = 0.2 * 0.1 = 0.02 → total = 0.10
    table = contingent_liability_shock(0.60, 0.80, 0.20, 0.10)
    total = [r[1] for r in table if r[0] == "total_contingent_shock_gdp"][0]
    assert abs(total - 0.10) < 1e-9


def test_contingent_liability_shock_post_debt():
    table = contingent_liability_shock(0.60, 0.80, 0.20, 0.10)
    post = [r[1] for r in table if r[0] == "post_shock_debt_gdp"][0]
    assert abs(post - 0.70) < 1e-9


def test_contingent_liability_shock_bad_rate():
    result = contingent_liability_shock(0.60, 0.80, 0.20, 1.5)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_fx_passthrough_basic():
    # 50 % FX share, 60 % debt/GDP, 20 % depreciation → 0.5 * 0.6 * 0.2 = 0.06
    result = exchange_rate_passthrough_to_debt(0.50, 0.60, 0.20)
    assert abs(result - 0.06) < 1e-9


def test_fx_passthrough_zero_share():
    result = exchange_rate_passthrough_to_debt(0.0, 0.80, 0.30)
    assert result == 0.0


def test_fx_passthrough_bad_share():
    result = exchange_rate_passthrough_to_debt(1.5, 0.60, 0.20)
    assert isinstance(result, str) and result.startswith("#ERR:")

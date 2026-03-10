from sovereign_debt_py.fiscal import (
    debt_stabilizing_primary_balance,
    debt_trajectory_forecast,
    fiscal_reaction_function,
    implicit_interest_rate,
)


def test_debt_trajectory_constant_debt():
    # When r == g and pb == 0 the ratio stays flat
    d0 = 0.60
    years = 5
    g = [0.03] * years
    r = [0.03] * years
    pb = [0.0] * years
    table = debt_trajectory_forecast(g, pb, r, d0, years)
    assert table[0] == ["year", "debt_gdp"]
    assert len(table) == years + 1
    for row in table[1:]:
        assert abs(row[1] - d0) < 1e-5


def test_debt_trajectory_rising():
    # High interest, no primary surplus → rising debt
    table = debt_trajectory_forecast([0.02], [0.0], [0.06], 0.5, 1)
    assert table[1][1] > 0.5


def test_debt_trajectory_short_path_error():
    result = debt_trajectory_forecast([0.02], [0.0], [0.03], 0.5, 3)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_fiscal_reaction_function_returns_table():
    # Synthetic data where pb responds positively to lagged debt
    pb = [0.01 * i + 0.005 * (0.5 + 0.05 * i) for i in range(10)]
    debt = [0.5 + 0.05 * i for i in range(10)]
    og = [0.01 * (i % 3 - 1) for i in range(10)]
    table = fiscal_reaction_function(pb, debt, og)
    assert table[0] == ["term", "coef", "pvalue"]
    terms = [r[0] for r in table]
    assert "lagged_debt" in terms
    assert "R2" in terms


def test_fiscal_reaction_too_few_obs():
    result = fiscal_reaction_function([0.01, 0.02, 0.03], [0.5, 0.6, 0.7], [0.0, 0.0, 0.0])
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_implicit_interest_rate_basic():
    # 5 paid on avg stock of 100 → 5 %
    rate = implicit_interest_rate(5.0, 100.0, 100.0)
    assert abs(rate - 0.05) < 1e-9


def test_implicit_interest_rate_zero_stock():
    result = implicit_interest_rate(5.0, 0.0, 0.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_debt_stabilizing_pb_formula():
    # pb* = d*(r-g)/(1+g)
    pb = debt_stabilizing_primary_balance(0.60, 0.05, 0.03)
    expected = 0.60 * (0.05 - 0.03) / (1.03)
    assert abs(pb - expected) < 1e-5


def test_debt_stabilizing_pb_zero_when_r_eq_g():
    pb = debt_stabilizing_primary_balance(0.60, 0.03, 0.03)
    assert abs(pb) < 1e-9

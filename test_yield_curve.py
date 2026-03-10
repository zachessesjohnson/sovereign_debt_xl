import math

from sovereign_debt_xl.yield_curve import asw_spread, carry_rolldown, nelson_siegel_fit, zspread

# ---------------------------------------------------------------------------
# Nelson-Siegel
# ---------------------------------------------------------------------------

def test_nelson_siegel_flat_curve():
    # A flat curve at 5 % should be recovered near perfectly
    maturities = [1.0, 2.0, 5.0, 10.0, 20.0, 30.0]
    yields = [0.05] * 6
    table = nelson_siegel_fit(maturities, yields)
    assert table[0] == ["metric", "value"]
    rmse_row = [r for r in table if r[0] == "rmse"][0]
    assert rmse_row[1] < 1e-4


def test_nelson_siegel_upward_slope():
    maturities = [1.0, 2.0, 5.0, 10.0, 30.0]
    yields = [0.02, 0.03, 0.04, 0.05, 0.06]
    table = nelson_siegel_fit(maturities, yields)
    b0_row = [r for r in table if r[0] == "beta0_level"][0]
    # Level parameter should be roughly near the long end
    assert b0_row[1] > 0.04


def test_nelson_siegel_too_few_points():
    result = nelson_siegel_fit([1.0, 2.0], [0.03, 0.04])
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# Z-spread
# ---------------------------------------------------------------------------

def test_zspread_par_bond_near_zero():
    tenors = [1.0, 2.0, 3.0, 4.0, 5.0]
    rates = [0.05] * 5
    # Compute the fair price under continuous discounting at 5% flat —
    # this is the price at which z-spread is exactly 0.
    par_price = sum(5.0 * math.exp(-0.05 * t) for t in range(1, 6)) + 100.0 * math.exp(-0.05 * 5)
    z = zspread(par_price, 5.0, 5.0, tenors, rates)
    assert abs(z) < 1e-6


def test_zspread_discount_bond_positive():
    # Bond priced below par → positive z-spread
    tenors = [1.0, 3.0, 5.0]
    rates = [0.04, 0.04, 0.04]
    z = zspread(95.0, 4.0, 5.0, tenors, rates)
    assert z > 0


def test_zspread_bad_inputs():
    result = zspread(-10.0, 5.0, 5.0, [1.0, 5.0], [0.04, 0.05])
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# Carry / rolldown
# ---------------------------------------------------------------------------

def test_carry_rolldown_structure():
    tenors = [1.0, 2.0, 5.0, 10.0, 30.0]
    rates = [0.02, 0.03, 0.04, 0.05, 0.06]
    table = carry_rolldown(5.0, tenors, rates, 12)
    assert table[0] == ["metric", "value"]
    keys = [r[0] for r in table]
    assert "carry" in keys
    assert "rolldown" in keys
    assert "total_return" in keys


def test_carry_rolldown_carry_positive():
    # Positive yield → positive carry
    tenors = [1.0, 5.0, 10.0]
    rates = [0.03, 0.04, 0.05]
    table = carry_rolldown(5.0, tenors, rates, 6)
    carry = [r[1] for r in table if r[0] == "carry"][0]
    assert carry > 0


# ---------------------------------------------------------------------------
# Asset-swap spread
# ---------------------------------------------------------------------------

def test_asw_spread_par_near_zero():
    tenors = [1.0, 2.0, 3.0, 5.0]
    rates = [0.04, 0.04, 0.04, 0.04]
    # Compute the OIS fair value — the price at which ASW is exactly 0.
    par_price = (
        sum(4.0 * math.exp(-0.04 * t) for t in range(1, 5))
        + 100.0 * math.exp(-0.04 * 4)
    )
    asw = asw_spread(par_price, 4.0, 4.0, tenors, rates)
    assert abs(asw) < 1e-5


def test_asw_spread_premium_bond_negative():
    # Bond priced above par (investor pays more) → negative ASW
    tenors = [1.0, 3.0, 5.0]
    rates = [0.03, 0.03, 0.03]
    asw = asw_spread(105.0, 4.0, 5.0, tenors, rates)
    assert asw < 0

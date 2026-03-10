import numpy as np

from sovereign_debt_xl.market_microstructure import (
    auction_tail_analysis,
    bid_ask_liquidity_score,
    investor_base_concentration,
    local_vs_external_curve_basis,
)


# ---------------------------------------------------------------------------
# bid_ask_liquidity_score
# ---------------------------------------------------------------------------

def test_liquidity_score_structure():
    ba = [5.0, 8.0, 3.0]
    to = [0.5, 0.8, 1.2]
    sz = [5.0, 10.0, 15.0]
    table = bid_ask_liquidity_score(ba, to, sz)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table if isinstance(r[0], str)]
    assert "composite_liquidity_score" in metrics


def test_liquidity_score_range():
    table = bid_ask_liquidity_score([10.0, 20.0], [0.3, 0.6], [8.0, 12.0])
    score = [r[1] for r in table if r[0] == "composite_liquidity_score"][0]
    assert 0.0 <= score <= 100.0


def test_liquidity_score_tight_market_higher():
    liquid = bid_ask_liquidity_score([1.0, 2.0], [1.8, 2.0], [18.0, 20.0])
    illiquid = bid_ask_liquidity_score([150.0, 180.0], [0.05, 0.03], [0.5, 0.3])
    liq_score = [r[1] for r in liquid if r[0] == "composite_liquidity_score"][0]
    ill_score = [r[1] for r in illiquid if r[0] == "composite_liquidity_score"][0]
    assert liq_score > ill_score


def test_liquidity_score_length_mismatch():
    result = bid_ask_liquidity_score([5.0, 8.0], [0.5], [5.0, 10.0])
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# local_vs_external_curve_basis
# ---------------------------------------------------------------------------

def test_local_external_basis_structure():
    lc = [0.08, 0.085, 0.09]
    xccy = [0.02, 0.025, 0.03]
    usd = [0.05, 0.055, 0.06]
    tenors = [2.0, 5.0, 10.0]
    table = local_vs_external_curve_basis(lc, xccy, usd, tenors)
    assert table[0] == ["tenor", "local_yield", "hedged_local_yield", "usd_yield", "basis_spread"]


def test_local_external_basis_values():
    # Hedged = 0.08 − 0.02 = 0.06; basis = 0.06 − 0.05 = 0.01
    table = local_vs_external_curve_basis([0.08], [0.02], [0.05], [5.0])
    assert abs(table[1][2] - 0.06) < 1e-6
    assert abs(table[1][4] - 0.01) < 1e-6


def test_local_external_basis_recommendation():
    # Positive average basis → local cheaper
    lc = [0.10, 0.11, 0.12]
    xccy = [0.01, 0.01, 0.01]
    usd = [0.05, 0.06, 0.07]
    tenors = [2.0, 5.0, 10.0]
    table = local_vs_external_curve_basis(lc, xccy, usd, tenors)
    recs = [r[4] for r in table if r[0] == "recommendation"]
    assert recs[0] == "local_cheaper"


# ---------------------------------------------------------------------------
# auction_tail_analysis
# ---------------------------------------------------------------------------

def test_auction_tail_structure():
    results = [[20250101, 2.0], [20250201, 3.5], [20250301, 2.8],
               [20250401, 4.1], [20250501, 5.0]]
    bc = [3.5, 3.2, 2.9, 2.7, 2.5]
    cwi = [1.0, 2.0, 1.5, 3.0, 4.0]
    table = auction_tail_analysis(results, bc, cwi)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    assert "demand_flag" in metrics


def test_auction_tail_too_few():
    result = auction_tail_analysis([[1, 2.0], [2, 3.0]], [3.0, 2.8], [1.0, 2.0])
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# investor_base_concentration
# ---------------------------------------------------------------------------

def test_hhi_equal_weights():
    # 4 equal holders → HHI = 0.25
    table = investor_base_concentration([25.0, 25.0, 25.0, 25.0])
    hhi = [r[1] for r in table if r[0] == "hhi_raw"][0]
    assert abs(hhi - 0.25) < 1e-6


def test_hhi_monopoly():
    # 1 holder → HHI = 1.0
    table = investor_base_concentration([100.0])
    hhi = [r[1] for r in table if r[0] == "hhi_raw"][0]
    assert abs(hhi - 1.0) < 1e-6


def test_hhi_concentration_flag():
    # Monopoly → HIGH
    table = investor_base_concentration([100.0])
    flag = [r[1] for r in table if r[0] == "concentration_flag"][0]
    assert flag == "HIGH"


def test_hhi_negative_input():
    result = investor_base_concentration([-10.0, 30.0])
    assert isinstance(result, str) and result.startswith("#ERR:")

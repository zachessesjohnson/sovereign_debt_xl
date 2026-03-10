from sovereign_debt_xl.amortization import (
    amortization_profile,
    gross_financing_need,
    weighted_avg_maturity,
)


# ---------------------------------------------------------------------------
# amortization_profile
# ---------------------------------------------------------------------------

def test_amortization_profile_sums_by_year():
    bonds = [[2025, 100.0], [2026, 200.0], [2025, 50.0], [2027, 150.0]]
    table = amortization_profile(bonds)
    assert table[0] == ["year", "redemption", "concentration_flag"]
    year_map = {r[0]: r[1] for r in table[1:]}
    assert abs(year_map[2025] - 150.0) < 1e-9
    assert abs(year_map[2026] - 200.0) < 1e-9


def test_amortization_profile_concentration_flag():
    # 2025: 300 out of 400 total = 75 % → HIGH
    bonds = [[2025, 300.0], [2026, 100.0]]
    table = amortization_profile(bonds)
    flags = {r[0]: r[2] for r in table[1:]}
    assert flags[2025] == "HIGH"
    assert flags[2026] == ""


def test_amortization_profile_skips_header():
    bonds = [["year", "face"], [2025, 500.0], [2026, 500.0]]
    table = amortization_profile(bonds)
    assert len(table) == 3  # header + 2 year rows


def test_amortization_profile_empty():
    result = amortization_profile([])
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# weighted_avg_maturity
# ---------------------------------------------------------------------------

def test_wam_equal_weights():
    # Two bonds with equal face: (2 + 5) / 2 = 3.5 years
    bonds = [[2.0, 100.0], [5.0, 100.0]]
    wam = weighted_avg_maturity(bonds)
    assert abs(wam - 3.5) < 1e-6


def test_wam_skewed():
    # Large long-dated bond dominates
    bonds = [[1.0, 10.0], [10.0, 90.0]]
    wam = weighted_avg_maturity(bonds)
    assert wam > 8.0


def test_wam_zero_face_value():
    result = weighted_avg_maturity([[5.0, 0.0], [10.0, 0.0]])
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# gross_financing_need
# ---------------------------------------------------------------------------

def test_gfn_basic():
    sched = [50.0, 60.0, 40.0]
    result = gross_financing_need(sched, 20.0, 2)
    assert abs(result - 80.0) < 1e-9


def test_gfn_year_out_of_range():
    result = gross_financing_need([50.0, 60.0], 20.0, 5)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_gfn_first_year():
    sched = [100.0, 80.0, 60.0]
    result = gross_financing_need(sched, 30.0, 1)
    assert abs(result - 130.0) < 1e-9

from sovereign_debt_xl.imf_framework import (
    dsa_replication,
    exceptional_access_criteria_check,
    imf_program_probability,
    sdrs_allocation_impact,
)


# ---------------------------------------------------------------------------
# dsa_replication
# ---------------------------------------------------------------------------

def test_dsa_replication_shape():
    gdp = [0.60, 0.03, 0.03, 0.03, 0.03, 0.03]
    pb = [0.01] * 5
    r = [0.05] * 5
    fx = [0.40]
    fa = [0.01, 0.005, 0.005, 0.40]
    table = dsa_replication(gdp, pb, r, fx, fa)
    assert table[0] == ["year", "baseline", "growth_shock", "pb_shock", "rate_shock", "fx_shock", "combined"]
    assert len(table) == 6  # header + 5 years


def test_dsa_baseline_rises_with_high_rates():
    # High interest rate, no primary surplus, should produce rising debt
    gdp = [0.60, 0.02, 0.02]
    pb = [0.0, 0.0]
    r = [0.08, 0.08]
    fx = [0.0]
    fa = [0.01, 0.005, 0.005]
    table = dsa_replication(gdp, pb, r, fx, fa)
    baseline_y2 = table[2][1]
    assert baseline_y2 > 0.60


def test_dsa_growth_shock_worse_than_baseline():
    gdp = [0.60, 0.03, 0.03, 0.03]
    pb = [0.01] * 3
    r = [0.05] * 3
    fx = [0.30]
    fa = [0.01, 0.005, 0.005]
    table = dsa_replication(gdp, pb, r, fx, fa)
    for row in table[1:]:
        assert row[2] >= row[1]  # growth shock >= baseline


def test_dsa_replication_bad_inputs():
    result = dsa_replication([0.60], [], [], [0.30], [0.01, 0.005, 0.005])
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# imf_program_probability
# ---------------------------------------------------------------------------

def test_imf_program_prob_stressed():
    # Very low reserves, very high debt, large CA deficit, high inflation, fixed FX, unstable politics
    p = imf_program_probability(1.0, 1.50, -0.10, 0.30, 1.0, -2.0)
    assert 0.0 < p <= 1.0
    assert p > 0.5


def test_imf_program_prob_stable():
    # High reserves, low debt, small CA surplus, low inflation, flexible FX, stable politics
    p = imf_program_probability(8.0, 0.30, 0.02, 0.02, 0.0, 2.0)
    assert 0.0 <= p < 0.5


def test_imf_program_prob_range():
    p = imf_program_probability(4.0, 0.80, -0.03, 0.07, 0.5, 0.0)
    assert 0.0 <= p <= 1.0


# ---------------------------------------------------------------------------
# exceptional_access_criteria_check
# ---------------------------------------------------------------------------

def test_exceptional_access_all_pass():
    table = exceptional_access_criteria_check(0.80, 0.25, 1.0, "SUSTAINABLE")
    overall = [r[1] for r in table if r[0] == "overall_exceptional_access"][0]
    assert overall == "PASS"


def test_exceptional_access_fail_debt():
    # Debt > 150 % → criterion 4 fails → overall fails
    table = exceptional_access_criteria_check(1.60, 0.25, 1.0, "SUSTAINABLE")
    overall = [r[1] for r in table if r[0] == "overall_exceptional_access"][0]
    assert overall == "FAIL"


def test_exceptional_access_structure():
    table = exceptional_access_criteria_check(0.90, 0.20, 1.0, "SUSTAINABLE_HIGH_PROBABILITY")
    criteria = [r[0] for r in table]
    assert "1_bop_need" in criteria
    assert "2_debt_sustainability" in criteria
    assert "3_market_access" in criteria
    assert "4_program_success" in criteria


# ---------------------------------------------------------------------------
# sdrs_allocation_impact
# ---------------------------------------------------------------------------

def test_sdrs_impact_reserves_increase():
    table = sdrs_allocation_impact(10.0, 500.0, 40.0, 4.0)
    pre = [r[1] for r in table if r[0] == "reserves"][0]
    post = [r[2] for r in table if r[0] == "reserves"][0]
    assert post > pre


def test_sdrs_impact_import_cover():
    # Reserves = 40, import cover = 4 months → monthly imports = 10
    # SDR = 10 → new reserves = 50 → new import cover = 5 months
    table = sdrs_allocation_impact(10.0, 500.0, 40.0, 4.0)
    ic_post = [r[2] for r in table if r[0] == "import_cover_months"][0]
    assert abs(ic_post - 5.0) < 1e-4


def test_sdrs_impact_bad_gdp():
    result = sdrs_allocation_impact(10.0, 0.0, 40.0, 4.0)
    assert isinstance(result, str) and result.startswith("#ERR:")

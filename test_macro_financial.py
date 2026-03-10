from sovereign_debt_xl.macro_financial import (
    dollarization_vulnerability,
    monetary_financing_risk,
    real_interest_rate_growth_differential,
    sovereign_bank_nexus_score,
)


# ---------------------------------------------------------------------------
# sovereign_bank_nexus_score
# ---------------------------------------------------------------------------

def test_nexus_score_structure():
    table = sovereign_bank_nexus_score(0.30, 0.20, 0.12, 400.0)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    assert "nexus_score_0_100" in metrics
    assert "doom_loop_flag" in metrics


def test_nexus_score_high_risk():
    # High bank holdings, high state ownership, low capital, high spread
    table = sovereign_bank_nexus_score(0.80, 0.70, 0.04, 900.0)
    score = [r[1] for r in table if r[0] == "nexus_score_0_100"][0]
    flag = [r[1] for r in table if r[0] == "doom_loop_flag"][0]
    assert score > 60
    assert flag == "HIGH"


def test_nexus_score_low_risk():
    # Low holdings, low state ownership, high capital, low spread
    table = sovereign_bank_nexus_score(0.05, 0.05, 0.18, 50.0)
    score = [r[1] for r in table if r[0] == "nexus_score_0_100"][0]
    assert score < 40


def test_nexus_score_bad_input():
    result = sovereign_bank_nexus_score(1.5, 0.20, 0.12, 400.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# monetary_financing_risk
# ---------------------------------------------------------------------------

def test_monetary_financing_structure():
    table = monetary_financing_risk(0.10, 0.15, 0.08, 0.70)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    assert "monetization_risk_score" in metrics
    assert "risk_flag" in metrics


def test_monetary_financing_high():
    # Very high CB claims, rapid reserve money growth, high inflation, low independence
    table = monetary_financing_risk(0.25, 0.50, 0.30, 0.05)
    score = [r[1] for r in table if r[0] == "monetization_risk_score"][0]
    assert score > 50


def test_monetary_financing_mitigated_by_independence():
    low_cbi = monetary_financing_risk(0.15, 0.20, 0.10, 0.10)
    high_cbi = monetary_financing_risk(0.15, 0.20, 0.10, 0.95)
    score_low = [r[1] for r in low_cbi if r[0] == "monetization_risk_score"][0]
    score_high = [r[1] for r in high_cbi if r[0] == "monetization_risk_score"][0]
    assert score_low > score_high


# ---------------------------------------------------------------------------
# real_interest_rate_growth_differential
# ---------------------------------------------------------------------------

def test_rg_differential_shape():
    nom = [0.06, 0.07, 0.065, 0.07, 0.075]
    infl = [0.03, 0.03, 0.035, 0.03, 0.03]
    g = [0.04, 0.035, 0.03, 0.04, 0.045]
    table = real_interest_rate_growth_differential(nom, infl, g, 4)
    assert table[0] == ["year", "r", "g", "r_minus_g", "rolling_avg_rg"]
    assert len(table) == 5  # header + 4 years


def test_rg_differential_values():
    # r = 0.06 − 0.03 = 0.03; g = 0.04 → r-g = −0.01
    table = real_interest_rate_growth_differential([0.06], [0.03], [0.04], 1)
    rg = table[1][3]
    assert abs(rg - (-0.01)) < 1e-6


def test_rg_differential_mismatch():
    result = real_interest_rate_growth_differential([0.05, 0.06], [0.03], [0.04, 0.04], 2)
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# dollarization_vulnerability
# ---------------------------------------------------------------------------

def test_dollarization_structure():
    table = dollarization_vulnerability(0.60, 0.55, 0.80)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    assert "dollarization_vulnerability_score" in metrics
    assert "vulnerability_flag" in metrics


def test_dollarization_high_risk():
    # High deposit dollarization, large mismatch, low FX coverage
    table = dollarization_vulnerability(0.90, 0.40, 0.20)
    score = [r[1] for r in table if r[0] == "dollarization_vulnerability_score"][0]
    assert score > 50


def test_dollarization_bad_input():
    result = dollarization_vulnerability(1.5, 0.40, 0.80)
    assert isinstance(result, str) and result.startswith("#ERR:")

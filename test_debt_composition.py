from sovereign_debt_xl.debt_composition import (
    collateralized_debt_flag,
    debt_transparency_score,
    hidden_debt_estimator,
    original_sin_index,
)


# ---------------------------------------------------------------------------
# original_sin_index
# ---------------------------------------------------------------------------

def test_original_sin_basic():
    table = original_sin_index(40.0, 100.0, 15.0)
    assert table[0] == ["metric", "value"]
    osin = [r[1] for r in table if r[0] == "original_sin_osin"][0]
    assert abs(osin - 0.40) < 1e-6


def test_original_sin_redux():
    # 30 % FX → 70 % local; 20 out of 70 held by non-residents → 0.2857
    table = original_sin_index(30.0, 100.0, 20.0)
    redux = [r[1] for r in table if r[0] == "original_sin_redux"][0]
    assert abs(redux - 20.0 / 70.0) < 1e-4


def test_original_sin_fx_exceeds_total():
    result = original_sin_index(110.0, 100.0, 0.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_original_sin_zero_total():
    result = original_sin_index(0.0, 0.0, 0.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# hidden_debt_estimator
# ---------------------------------------------------------------------------

def test_hidden_debt_total():
    table = hidden_debt_estimator(100.0, 20.0, 10.0, 5.0, 8.0)
    aug = [r[1] for r in table if r[0] == "augmented_debt"][0]
    assert abs(aug - 143.0) < 1e-6


def test_hidden_debt_pct():
    table = hidden_debt_estimator(100.0, 20.0, 10.0, 5.0, 8.0)
    pct = [r[1] for r in table if r[0] == "hidden_debt_pct_of_reported"][0]
    assert abs(pct - 43.0) < 1e-6


def test_hidden_debt_negative_component():
    result = hidden_debt_estimator(100.0, -5.0, 0.0, 0.0, 0.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# debt_transparency_score
# ---------------------------------------------------------------------------

def test_transparency_score_perfect():
    table = debt_transparency_score(1.0, 1.0, 1.0, 1.0, 1.0)
    score = [r[1] for r in table if r[0] == "transparency_score_0_100"][0]
    assert abs(score - 100.0) < 1e-6


def test_transparency_score_zero():
    table = debt_transparency_score(0.0, 0.0, 0.0, 0.0, 0.0)
    score = [r[1] for r in table if r[0] == "transparency_score_0_100"][0]
    assert abs(score) < 1e-6


def test_transparency_score_flags():
    table = debt_transparency_score(0.0, 0.0, 0.0, 0.0, 0.0)
    flags_row = [r[1] for r in table if r[0] == "flags"][0]
    assert "NOT_SDDS_SUBSCRIBER" in flags_row


def test_transparency_score_out_of_range():
    result = debt_transparency_score(2.0, 1.0, 1.0, 1.0, 1.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# collateralized_debt_flag
# ---------------------------------------------------------------------------

def test_collateralized_flag_high():
    # 30 % resource-backed → HIGH
    table = collateralized_debt_flag(30.0, 100.0, 50.0, "oil")
    flag = [r[1] for r in table if r[0] == "concentration_risk_flag"][0]
    assert flag == "HIGH"


def test_collateralized_flag_low():
    # 5 % → LOW
    table = collateralized_debt_flag(5.0, 100.0, 80.0, "copper")
    flag = [r[1] for r in table if r[0] == "concentration_risk_flag"][0]
    assert flag == "LOW"


def test_collateralized_pledged_share():
    table = collateralized_debt_flag(20.0, 100.0, 40.0, "oil")
    pledged = [r[1] for r in table if r[0] == "pledged_share_of_exports"][0]
    assert abs(pledged - 0.50) < 1e-6

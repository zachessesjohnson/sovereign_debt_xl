from sovereign_debt_xl.political_esg import (
    esg_sovereign_score,
    political_risk_score,
    sanctions_exposure_index,
)


# ---------------------------------------------------------------------------
# political_risk_score
# ---------------------------------------------------------------------------

def test_political_risk_score_structure():
    table = political_risk_score(-5.0, [-1.0, -0.5, 0.0, 0.5, 1.0, 0.5], 3.0, 0.0, 18.0)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    assert "composite_score_0_100" in metrics


def test_political_risk_score_range():
    table = political_risk_score(8.0, [1.5, 1.2, 0.8, 1.0, 0.9, 1.1], 15.0, 0.0, 48.0)
    score = [r[1] for r in table if r[0] == "composite_score_0_100"][0]
    assert 0.0 <= score <= 100.0


def test_political_risk_score_empty_wgi():
    result = political_risk_score(5.0, [], 10.0, 0.0, 24.0)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_political_risk_high_vs_low():
    # Stressed: autocratic, low governance, recent default, regime change, election imminent
    stressed = political_risk_score(-10.0, [-2.0, -2.0, -2.0, -2.0, -2.0, -2.0], 0.0, 1.0, 0.0)
    # Stable: democratic, strong governance, no default for 20 years
    stable = political_risk_score(10.0, [2.0, 2.0, 2.0, 2.0, 2.0, 2.0], 20.0, 0.0, 48.0)
    stressed_score = [r[1] for r in stressed if r[0] == "composite_score_0_100"][0]
    stable_score = [r[1] for r in stable if r[0] == "composite_score_0_100"][0]
    assert stressed_score > stable_score


# ---------------------------------------------------------------------------
# esg_sovereign_score
# ---------------------------------------------------------------------------

def test_esg_sovereign_score_structure():
    table = esg_sovereign_score(5.0, 0.30, 0.38, 0.5, 0.05, 0.06)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    for m in ["composite_esg_score", "environmental_pillar", "social_pillar", "governance_pillar"]:
        assert m in metrics


def test_esg_composite_in_range():
    table = esg_sovereign_score(3.0, 0.50, 0.32, 1.2, 0.06, 0.07)
    score = [r[1] for r in table if r[0] == "composite_esg_score"][0]
    assert 0.0 <= score <= 100.0


def test_esg_green_country_higher():
    # Low CO2, high renewables, low gini, strong rule of law, high spending
    green = esg_sovereign_score(1.0, 0.80, 0.25, 2.0, 0.09, 0.09)
    # High CO2, low renewables, high gini, weak rule of law, low spending
    poor = esg_sovereign_score(18.0, 0.05, 0.65, -2.0, 0.02, 0.02)
    green_score = [r[1] for r in green if r[0] == "composite_esg_score"][0]
    poor_score = [r[1] for r in poor if r[0] == "composite_esg_score"][0]
    assert green_score > poor_score


# ---------------------------------------------------------------------------
# sanctions_exposure_index
# ---------------------------------------------------------------------------

def test_sanctions_exposure_structure():
    table = sanctions_exposure_index([0.6, 0.4], [0.5, 0.3, 0.2], 0.85, 0.40)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table]
    assert "sanctions_exposure_index" in metrics


def test_sanctions_exposure_concentrated_higher():
    # Single trade partner + single FX currency = max concentration
    conc = sanctions_exposure_index([1.0], [1.0], 1.0, 1.0)
    # Diversified
    div = sanctions_exposure_index([0.25, 0.25, 0.25, 0.25], [0.25, 0.25, 0.25, 0.25], 0.2, 0.1)
    conc_score = [r[1] for r in conc if r[0] == "sanctions_exposure_index"][0]
    div_score = [r[1] for r in div if r[0] == "sanctions_exposure_index"][0]
    assert conc_score > div_score

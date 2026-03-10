from __future__ import annotations

from typing import Any

import numpy as np

from ._coerce import safe_err, to_1d_floats


def political_risk_score(
    polity_iv_score: float,
    wgi_governance_indicators: Any,
    years_since_last_default: float,
    regime_change_dummy: float,
    election_proximity_months: float,
) -> list[list[Any]] | str:
    """Composite political risk index via PCA-inspired weighting of institutional inputs.

    Returns a 0–100 score (higher = more risk) and each input's contribution.
    Polity IV: ranges roughly −10 (autocracy) to +10 (democracy).
    WGI indicators: six World Bank governance scores, each in [−2.5, +2.5].
    years_since_last_default: 0 if currently in default.
    regime_change_dummy: 1 if a regime change occurred within the past 2 years.
    election_proximity_months: months until next scheduled election (lower = more risk).
    """
    try:
        wgi = to_1d_floats(wgi_governance_indicators)
        if len(wgi) == 0:
            return safe_err(ValueError("wgi_governance_indicators must not be empty"))
        polity = float(polity_iv_score)
        ysd = float(years_since_last_default)
        rc = float(regime_change_dummy)
        epm = float(election_proximity_months)

        # Normalise each input to a 0–100 risk scale (higher = more risky)
        # Polity: −10 → 100 (fully autocratic = most risk), +10 → 0
        polity_risk = float(np.clip((10.0 - polity) / 20.0 * 100.0, 0.0, 100.0))
        # WGI: mean governance. −2.5 → 100 risk, +2.5 → 0 risk
        wgi_mean = float(np.mean(wgi))
        wgi_risk = float(np.clip((-wgi_mean + 2.5) / 5.0 * 100.0, 0.0, 100.0))
        # Default history: 0 years → 100 risk, diminishing over 20 years
        default_risk = float(np.clip(100.0 - ysd / 20.0 * 100.0, 0.0, 100.0))
        # Regime change: binary, 100 if 1
        regime_risk = float(np.clip(rc, 0.0, 1.0)) * 100.0
        # Election proximity: 0 months → 100 risk, ≥ 24 → 0 risk
        election_risk = float(np.clip(100.0 - epm / 24.0 * 100.0, 0.0, 100.0))

        # Weights informed by empirical sovereign risk literature
        weights = np.array([0.30, 0.30, 0.20, 0.10, 0.10])
        components = np.array([polity_risk, wgi_risk, default_risk, regime_risk, election_risk])
        score = float(np.dot(weights, components))

        labels = ["polity_risk", "wgi_risk", "default_history_risk", "regime_change_risk", "election_risk"]
        out: list[list[Any]] = [["metric", "value"]]
        out.append(["composite_score_0_100", round(score, 2)])
        for lbl, val, w in zip(labels, components.tolist(), weights.tolist()):
            out.append([lbl, round(val, 2)])
            out.append([f"{lbl}_weight", round(w, 4)])
        return out
    except Exception as e:
        return safe_err(e)


def esg_sovereign_score(
    co2_per_capita: float,
    renewable_energy_share: float,
    gini_coefficient: float,
    rule_of_law_index: float,
    education_spending_gdp: float,
    health_spending_gdp: float,
) -> list[list[Any]] | str:
    """Weighted composite ESG score calibrated to sovereign credit outcomes.

    Returns pillar scores (E, S, G) and a composite 0–100 score.
    Higher composite score = better ESG profile.
    Weights derived from academic literature linking ESG to sovereign spreads.
    """
    try:
        co2 = float(co2_per_capita)
        ren = float(renewable_energy_share)
        gini = float(gini_coefficient)
        rol = float(rule_of_law_index)
        edu = float(education_spending_gdp)
        hlt = float(health_spending_gdp)

        # Environmental pillar (0–100, higher = better)
        # CO2 per capita: 0 t → 100, 20+ t → 0 (global mean ~4 t)
        e_co2 = float(np.clip(100.0 - co2 / 20.0 * 100.0, 0.0, 100.0))
        # Renewable share: 0 % → 0, 100 % → 100
        e_ren = float(np.clip(ren * 100.0, 0.0, 100.0)) if ren <= 1.0 else float(np.clip(ren, 0.0, 100.0))
        e_pillar = (e_co2 + e_ren) / 2.0

        # Social pillar (0–100, higher = better)
        # Gini: 0 → 100, 1 (or 100) → 0
        gini_norm = gini if gini <= 1.0 else gini / 100.0
        s_gini = float(np.clip((1.0 - gini_norm) * 100.0, 0.0, 100.0))
        # Education & health spending as % GDP — 0 % → 0, 10 %+ → 100 each
        s_edu = float(np.clip(edu / 10.0 * 100.0, 0.0, 100.0))
        s_hlt = float(np.clip(hlt / 10.0 * 100.0, 0.0, 100.0))
        s_pillar = (s_gini + s_edu + s_hlt) / 3.0

        # Governance pillar (0–100, higher = better)
        # Rule of law: WB index −2.5 → 0, +2.5 → 100
        g_rol = float(np.clip((rol + 2.5) / 5.0 * 100.0, 0.0, 100.0))
        g_pillar = g_rol

        # Composite with typical sovereign-ESG weights E:20%, S:35%, G:45%
        composite = 0.20 * e_pillar + 0.35 * s_pillar + 0.45 * g_pillar

        return [
            ["metric", "value"],
            ["composite_esg_score", round(composite, 2)],
            ["environmental_pillar", round(e_pillar, 2)],
            ["social_pillar", round(s_pillar, 2)],
            ["governance_pillar", round(g_pillar, 2)],
            ["e_co2_score", round(e_co2, 2)],
            ["e_renewable_score", round(e_ren, 2)],
            ["s_gini_score", round(s_gini, 2)],
            ["s_education_score", round(s_edu, 2)],
            ["s_health_score", round(s_hlt, 2)],
            ["g_rule_of_law_score", round(g_rol, 2)],
        ]
    except Exception as e:
        return safe_err(e)


def sanctions_exposure_index(
    trade_partner_shares: Any,
    fx_reserves_by_currency_share: Any,
    swift_dependency_pct: float,
    energy_export_share: float,
) -> list[list[Any]] | str:
    """Quantify a sovereign's vulnerability to financial sanctions.

    Inputs:
    - trade_partner_shares: share of trade with potentially sanctioning partners
    - fx_reserves_by_currency_share: share of FX reserves in sanctionable currencies
    - swift_dependency_pct: share of cross-border payments routed through SWIFT
    - energy_export_share: share of total exports from energy commodities

    Returns a 0–100 exposure index (higher = more vulnerable).
    """
    try:
        trade_shares = to_1d_floats(trade_partner_shares)
        fx_shares = to_1d_floats(fx_reserves_by_currency_share)
        swift = float(swift_dependency_pct)
        energy = float(energy_export_share)

        if not trade_shares:
            return safe_err(ValueError("trade_partner_shares must not be empty"))
        if not fx_shares:
            return safe_err(ValueError("fx_reserves_by_currency_share must not be empty"))

        # Herfindahl-based concentration in trade partners (higher HHI = more concentrated = more risk)
        arr_t = np.array(trade_shares, dtype=float)
        if arr_t.sum() > 0:
            arr_t = arr_t / arr_t.sum()
        trade_hhi = float(np.sum(arr_t**2))  # 0–1
        trade_score = trade_hhi * 100.0

        # FX reserves concentration
        arr_f = np.array(fx_shares, dtype=float)
        if arr_f.sum() > 0:
            arr_f = arr_f / arr_f.sum()
        fx_hhi = float(np.sum(arr_f**2))
        fx_score = fx_hhi * 100.0

        # SWIFT dependency (already a percentage, normalise to 0–100)
        swift_norm = swift if swift <= 1.0 else swift  # accept both % and decimal
        swift_score = float(np.clip(swift_norm * 100.0 if swift_norm <= 1.0 else swift_norm, 0.0, 100.0))

        # Energy export share
        energy_norm = energy if energy <= 1.0 else energy / 100.0
        energy_score = float(np.clip(energy_norm * 100.0, 0.0, 100.0))

        # Equal-weighted composite
        composite = (trade_score + fx_score + swift_score + energy_score) / 4.0

        return [
            ["metric", "value"],
            ["sanctions_exposure_index", round(composite, 2)],
            ["trade_concentration_score", round(trade_score, 2)],
            ["fx_reserves_concentration_score", round(fx_score, 2)],
            ["swift_dependency_score", round(swift_score, 2)],
            ["energy_export_score", round(energy_score, 2)],
        ]
    except Exception as e:
        return safe_err(e)

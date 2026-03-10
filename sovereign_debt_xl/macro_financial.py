from __future__ import annotations

from typing import Any

import numpy as np
from pyxll import xl_func

from ._coerce import safe_err, to_1d_floats


@xl_func(
    "float bank_holdings_of_govt_debt, float govt_ownership_of_banks,"
    " float bank_capital_ratio, float sovereign_spread_bps: object[][]",
    name="SOV_BANK_NEXUS_SCORE",
)
def sovereign_bank_nexus_score(
    bank_holdings_of_govt_debt: float,
    govt_ownership_of_banks: float,
    bank_capital_ratio: float,
    sovereign_spread_bps: float,
) -> list[list[Any]] | str:
    """Quantify the sovereign–bank doom-loop risk.

    Returns a composite nexus score (0–100; higher = stronger doom loop).

    Inputs:
    - bank_holdings_of_govt_debt: banks' govt bond holdings as % of bank assets (0–1)
    - govt_ownership_of_banks: share of banking assets under state ownership (0–1)
    - bank_capital_ratio: Tier-1 capital ratio (0–1; higher = more resilient)
    - sovereign_spread_bps: current CDS / EMBI spread in basis points
    """
    try:
        bh = float(bank_holdings_of_govt_debt)
        go = float(govt_ownership_of_banks)
        bcr = float(bank_capital_ratio)
        spread = float(sovereign_spread_bps)
        for name, val in [("bank_holdings", bh), ("govt_ownership", go), ("bank_capital_ratio", bcr)]:
            if not (0.0 <= val <= 1.0):
                return safe_err(ValueError(f"{name} must be in [0, 1]"))
        if spread < 0:
            return safe_err(ValueError("sovereign_spread_bps must be >= 0"))
        # Risk factors: high holdings, high state ownership, low capital → high score
        holdings_score = bh * 100.0
        ownership_score = go * 100.0
        capital_score = (1.0 - bcr) * 100.0  # low capital = high risk
        spread_score = float(np.clip(spread / 1000.0 * 100.0, 0.0, 100.0))  # 1000 bps caps at 100
        # Weights: holdings 35%, ownership 20%, capital 30%, spread 15%
        composite = 0.35 * holdings_score + 0.20 * ownership_score + 0.30 * capital_score + 0.15 * spread_score
        doom_loop_flag = "HIGH" if composite > 60 else ("MEDIUM" if composite > 35 else "LOW")
        return [
            ["metric", "value"],
            ["nexus_score_0_100", round(composite, 2)],
            ["doom_loop_flag", doom_loop_flag],
            ["bank_holdings_score", round(holdings_score, 2)],
            ["govt_ownership_score", round(ownership_score, 2)],
            ["bank_capital_resilience_score", round(capital_score, 2)],
            ["spread_stress_score", round(spread_score, 2)],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float central_bank_claims_on_govt, float reserve_money_growth,"
    " float inflation_rate, float cb_independence_index: object[][]",
    name="SOV_MONETARY_FINANCING_RISK",
)
def monetary_financing_risk(
    central_bank_claims_on_govt: float,
    reserve_money_growth: float,
    inflation_rate: float,
    cb_independence_index: float,
) -> list[list[Any]] | str:
    """Flag probability of debt monetization.

    Scores central bank balance sheet exposure against institutional safeguards.
    Returns a 0–100 monetization risk score.

    Inputs:
    - central_bank_claims_on_govt: CB claims on government as % of GDP (0–1)
    - reserve_money_growth: annual reserve money growth rate (decimal)
    - inflation_rate: annual CPI inflation rate (decimal)
    - cb_independence_index: 0 = fully dependent, 1 = fully independent
    """
    try:
        cb_claims = float(central_bank_claims_on_govt)
        rm_growth = float(reserve_money_growth)
        infl = float(inflation_rate)
        cbi = float(cb_independence_index)
        if not (0.0 <= cbi <= 1.0):
            return safe_err(ValueError("cb_independence_index must be in [0, 1]"))
        # Claims score: 0 % → 0, 20 %+ → 100
        claims_score = float(np.clip(cb_claims / 0.20 * 100.0, 0.0, 100.0))
        # Reserve money growth score: 0 % → 0, 50 %+ → 100
        rm_score = float(np.clip(rm_growth / 0.50 * 100.0, 0.0, 100.0))
        # Inflation score: 0 % → 0, 20 %+ → 100
        infl_score = float(np.clip(infl / 0.20 * 100.0, 0.0, 100.0))
        # Independence mitigant: high independence lowers risk (scaled 0→+50 mitigation)
        independence_mitigation = cbi * 50.0
        raw = (claims_score * 0.40 + rm_score * 0.30 + infl_score * 0.30)
        composite = float(np.clip(raw - independence_mitigation, 0.0, 100.0))
        flag = "HIGH" if composite > 60 else ("MEDIUM" if composite > 30 else "LOW")
        return [
            ["metric", "value"],
            ["monetization_risk_score", round(composite, 2)],
            ["risk_flag", flag],
            ["cb_claims_score", round(claims_score, 2)],
            ["reserve_money_growth_score", round(rm_score, 2)],
            ["inflation_score", round(infl_score, 2)],
            ["independence_mitigation", round(independence_mitigation, 2)],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[] nominal_rate, float[] inflation, float[] real_gdp_growth, int years: object[][]",
    name="SOV_RG_DIFFERENTIAL",
)
def real_interest_rate_growth_differential(
    nominal_rate: Any,
    inflation: Any,
    real_gdp_growth: Any,
    years: int,
) -> list[list[Any]] | str:
    """Compute the r−g time series and its rolling average.

    r−g is the single most important driver of long-run debt dynamics.
    Real interest rate r = nominal_rate − inflation (Fisher approximation).

    Returns each period's r−g and the cumulative rolling average.
    """
    try:
        nom = np.array(to_1d_floats(nominal_rate), dtype=float)
        infl = np.array(to_1d_floats(inflation), dtype=float)
        g = np.array(to_1d_floats(real_gdp_growth), dtype=float)
        n = len(nom)
        if n == 0:
            return safe_err(ValueError("nominal_rate must not be empty"))
        if len(infl) != n or len(g) != n:
            return safe_err(ValueError("All series must have the same length"))
        if years < 1 or years > n:
            return safe_err(ValueError(f"years must be in [1, {n}]"))
        r_real = nom[:years] - infl[:years]
        g_sub = g[:years]
        rg = r_real - g_sub
        rolling_avg = np.cumsum(rg) / np.arange(1, years + 1)
        out: list[list[Any]] = [["year", "r", "g", "r_minus_g", "rolling_avg_rg"]]
        for t in range(years):
            out.append([
                t + 1,
                round(float(r_real[t]), 6),
                round(float(g_sub[t]), 6),
                round(float(rg[t]), 6),
                round(float(rolling_avg[t]), 6),
            ])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float deposit_dollarization_pct, float loan_dollarization_pct,"
    " float fx_reserves_to_fx_deposits: object[][]",
    name="SOV_DOLLARIZATION_VULNERABILITY",
)
def dollarization_vulnerability(
    deposit_dollarization_pct: float,
    loan_dollarization_pct: float,
    fx_reserves_to_fx_deposits: float,
) -> list[list[Any]] | str:
    """Assess balance sheet mismatches in highly dollarized economies.

    A devaluation triggers systemic stress when FX deposits are large relative
    to FX reserves.

    Inputs:
    - deposit_dollarization_pct: share of bank deposits in foreign currency (0–1)
    - loan_dollarization_pct: share of bank loans in foreign currency (0–1)
    - fx_reserves_to_fx_deposits: FX reserves / total FX deposits (liquidity buffer)

    Returns a vulnerability score (0–100) and sub-indicators.
    """
    try:
        dep_dol = float(deposit_dollarization_pct)
        loan_dol = float(loan_dollarization_pct)
        fx_cov = float(fx_reserves_to_fx_deposits)
        for name, val in [("deposit_dollarization_pct", dep_dol), ("loan_dollarization_pct", loan_dol)]:
            if not (0.0 <= val <= 1.0):
                return safe_err(ValueError(f"{name} must be in [0, 1]"))
        if fx_cov < 0:
            return safe_err(ValueError("fx_reserves_to_fx_deposits must be >= 0"))
        # Mismatch: difference between loan and deposit dollarization
        mismatch = abs(loan_dol - dep_dol)
        mismatch_score = mismatch * 100.0
        deposit_score = dep_dol * 100.0
        # Coverage ratio: < 0.5 → high risk, > 1.5 → low risk
        coverage_score = float(np.clip((1.5 - fx_cov) / 1.5 * 100.0, 0.0, 100.0))
        composite = 0.35 * deposit_score + 0.25 * mismatch_score + 0.40 * coverage_score
        flag = "HIGH" if composite > 60 else ("MEDIUM" if composite > 35 else "LOW")
        return [
            ["metric", "value"],
            ["dollarization_vulnerability_score", round(composite, 2)],
            ["vulnerability_flag", flag],
            ["deposit_dollarization_score", round(deposit_score, 2)],
            ["loan_deposit_mismatch_score", round(mismatch_score, 2)],
            ["fx_coverage_score", round(coverage_score, 2)],
            ["fx_deposit_coverage_ratio", round(fx_cov, 4)],
        ]
    except Exception as e:
        return safe_err(e)

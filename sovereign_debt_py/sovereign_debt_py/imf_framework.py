from __future__ import annotations

from typing import Any

import numpy as np
from scipy.special import expit

from ._coerce import safe_err, to_1d_floats


def dsa_replication(
    gdp_path: Any,
    fiscal_path: Any,
    interest_path: Any,
    exchange_rate_path: Any,
    financing_assumptions: Any,
) -> list[list[Any]] | str:
    """Replicate the IMF Debt Sustainability Analysis framework.

    Runs the baseline plus five standardised stress tests:
    1. Growth shock (−1 std dev)
    2. Primary balance shock (−1 std dev)
    3. Interest rate shock (+1 std dev)
    4. Exchange rate shock (30 % depreciation)
    5. Combined shock (all four simultaneously at 50 % magnitude)

    Inputs:
    - gdp_path: [initial_debt_gdp, gdp_growth_y1, gdp_growth_y2, ...]
    - fiscal_path: [primary_balance_y1, primary_balance_y2, ...]
    - interest_path: [interest_rate_y1, interest_rate_y2, ...]
    - exchange_rate_path: [fx_debt_share, depreciation_y1, depreciation_y2, ...]
    - financing_assumptions: [shock_std_gdp, shock_std_pb, shock_std_rate, fx_debt_share_override]
      (override can be set to NaN to use exchange_rate_path[0])

    Returns debt-to-GDP paths for baseline and each stress test.
    """
    try:
        gdp_raw = to_1d_floats(gdp_path)
        pb_raw = to_1d_floats(fiscal_path)
        r_raw = to_1d_floats(interest_path)
        fx_raw = to_1d_floats(exchange_rate_path)
        fa = to_1d_floats(financing_assumptions)
        if len(gdp_raw) < 2:
            return safe_err(ValueError("gdp_path needs [initial_debt_gdp, growth_y1, ...]"))
        d0 = gdp_raw[0]
        g = gdp_raw[1:]
        years = min(len(g), len(pb_raw), len(r_raw))
        if years < 1:
            return safe_err(ValueError("Need at least 1 projection year in all paths"))
        g = g[:years]
        pb = np.array(pb_raw[:years], dtype=float)
        r = np.array(r_raw[:years], dtype=float)
        if len(fa) < 3:
            return safe_err(ValueError("financing_assumptions needs at least 3 values: [std_g, std_pb, std_r]"))
        std_g, std_pb, std_r = fa[0], fa[1], fa[2]
        fx_share = fx_raw[0] if fx_raw else 0.0

        def project(g_arr, pb_arr, r_arr, d_init, fx_dep=None):
            d = d_init
            path = []
            for t in range(years):
                denom = 1.0 + g_arr[t]
                d = d * (1.0 + r_arr[t]) / denom - pb_arr[t] if denom != 0 else d
                if fx_dep is not None:
                    d += fx_share * d_init * fx_dep[t]
                path.append(round(d, 4))
            return path

        g_arr = np.array(g, dtype=float)
        base = project(g_arr, pb, r, d0)
        shock_g = project(g_arr - std_g, pb, r, d0)
        shock_pb = project(g_arr, pb - std_pb, r, d0)
        shock_r = project(g_arr, pb, r + std_r, d0)
        fx_dep = np.array([0.30] + [0.0] * (years - 1))
        shock_fx = project(g_arr, pb, r, d0, fx_dep=fx_dep)
        combined = project(g_arr - 0.5 * std_g, pb - 0.5 * std_pb, r + 0.5 * std_r, d0,
                           fx_dep=np.array([0.15] + [0.0] * (years - 1)))
        out: list[list[Any]] = [["year", "baseline", "growth_shock", "pb_shock", "rate_shock", "fx_shock", "combined"]]
        for t in range(years):
            out.append([t + 1, base[t], shock_g[t], shock_pb[t], shock_r[t], shock_fx[t], combined[t]])
        return out
    except Exception as e:
        return safe_err(e)


def imf_program_probability(
    reserves_months_imports: float,
    debt_gdp: float,
    current_account_gdp: float,
    inflation: float,
    exchange_rate_regime: float,
    political_stability: float,
) -> float | str:
    """Probability of IMF program entry within 24 months.

    Uses a logistic regression model calibrated on stylised coefficients from
    the empirical literature (Bird & Rowlands, Bal Gunduz et al.).

    Inputs:
    - reserves_months_imports: import cover (lower → more likely)
    - debt_gdp: debt-to-GDP (higher → more likely)
    - current_account_gdp: CA balance as % GDP (more negative → more likely)
    - inflation: annual CPI inflation (higher → more likely)
    - exchange_rate_regime: 1 = fixed, 0 = flexible (fixed → more likely)
    - political_stability: WB index −2.5 to +2.5 (lower → more likely)

    Returns a probability in [0, 1].
    """
    try:
        rim = float(reserves_months_imports)
        dg = float(debt_gdp)
        ca = float(current_account_gdp)
        infl = float(inflation)
        er = float(exchange_rate_regime)
        ps = float(political_stability)
        # Calibrated coefficients (stylised, based on published literature)
        intercept = -3.50
        coef_reserves = -0.25      # lower reserves → higher risk
        coef_debt = 1.80           # higher debt → higher risk
        coef_ca = -3.00            # more negative CA → higher risk
        coef_infl = 2.50           # higher inflation → higher risk
        coef_regime = 0.40         # fixed regime → higher risk
        coef_polstab = -0.35       # lower stability → higher risk
        logit = (intercept
                 + coef_reserves * rim
                 + coef_debt * dg
                 + coef_ca * ca
                 + coef_infl * infl
                 + coef_regime * er
                 + coef_polstab * ps)
        prob = float(expit(logit))
        return round(prob, 4)
    except Exception as e:
        return safe_err(e)


def exceptional_access_criteria_check(
    debt_gdp: float,
    gross_financing_need_gdp: float,
    market_access_boolean: float,
    debt_sustainability_assessment: str,
) -> list[list[Any]] | str:
    """Evaluate whether a sovereign meets IMF exceptional access criteria.

    The four criteria (as per IMF 2016 framework):
    1. Balance of payments need — proxied by GFN/GDP > 15 %
    2. Debt sustainability (with high probability) — passed-in as string
    3. Market access — can the country raise financing at reasonable cost?
    4. Prospects for success — proxied by debt/GDP < 150 %

    Returns PASS/FAIL for each criterion.
    """
    try:
        dg = float(debt_gdp)
        gfn = float(gross_financing_need_gdp)
        mkt = float(market_access_boolean)
        dsa = str(debt_sustainability_assessment).strip().upper()
        # Criterion 1: BoP need (GFN/GDP > 15 %)
        c1_pass = gfn > 0.15
        # Criterion 2: Debt sustainability with high probability
        c2_pass = dsa in ("SUSTAINABLE", "SUSTAINABLE_HIGH_PROBABILITY", "YES", "TRUE", "1")
        # Criterion 3: Market access (1 = yes, 0 = no); need access to remain (pass if accessible)
        c3_pass = mkt >= 0.5
        # Criterion 4: Debt not unsustainable — proxy: debt/GDP < 150 %
        c4_pass = dg < 1.50
        all_pass = c1_pass and c2_pass and c3_pass and c4_pass
        return [
            ["criterion", "result", "description"],
            ["1_bop_need", "PASS" if c1_pass else "FAIL", f"GFN/GDP {round(gfn * 100, 1)} % > 15 %"],
            ["2_debt_sustainability", "PASS" if c2_pass else "FAIL", f"DSA: {dsa}"],
            ["3_market_access", "PASS" if c3_pass else "FAIL", f"Market access: {'yes' if mkt >= 0.5 else 'no'}"],
            ["4_program_success", "PASS" if c4_pass else "FAIL", f"Debt/GDP {round(dg * 100, 1)} % < 150 %"],
            ["overall_exceptional_access", "PASS" if all_pass else "FAIL", ""],
        ]
    except Exception as e:
        return safe_err(e)


def sdrs_allocation_impact(
    sdr_allocation: float,
    gdp: float,
    reserves: float,
    import_cover_pre: float,
) -> list[list[Any]] | str:
    """Marginal improvement to reserve adequacy from an SDR allocation.

    Computes the post-allocation change in: reserves/GDP, Greenspan-Guidotti
    (placeholder, since STD not provided), and import cover.
    Assumes one-for-one pass-through of SDRs to usable reserves.
    """
    try:
        sdr = float(sdr_allocation)
        g = float(gdp)
        res = float(reserves)
        ic_pre = float(import_cover_pre)
        if g <= 0:
            return safe_err(ValueError("gdp must be > 0"))
        if sdr < 0 or res < 0 or ic_pre < 0:
            return safe_err(ValueError("sdr_allocation, reserves, and import_cover_pre must be >= 0"))
        new_reserves = res + sdr
        delta_res = sdr
        reserves_gdp_pre = res / g
        reserves_gdp_post = new_reserves / g
        # Import cover: assume ic_pre = res / monthly_imports
        # monthly_imports = res / ic_pre (if ic_pre > 0)
        if ic_pre > 0:
            monthly_imports = res / ic_pre
            ic_post = new_reserves / monthly_imports
            ic_change = ic_post - ic_pre
        else:
            ic_post = float("nan")
            ic_change = float("nan")
        return [
            ["metric", "pre_allocation", "post_allocation", "change"],
            ["reserves", round(res, 4), round(new_reserves, 4), round(delta_res, 4)],
            ["reserves_pct_gdp", round(reserves_gdp_pre * 100, 2), round(reserves_gdp_post * 100, 2),
             round((reserves_gdp_post - reserves_gdp_pre) * 100, 2)],
            ["import_cover_months", round(ic_pre, 2),
             round(ic_post, 2) if ic_pre > 0 else float("nan"),
             round(ic_change, 2) if ic_pre > 0 else float("nan")],
            ["sdr_allocation_gdp_pct", "", round(sdr / g * 100, 2), ""],
        ]
    except Exception as e:
        return safe_err(e)

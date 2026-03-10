from __future__ import annotations

from typing import Any

import numpy as np
import statsmodels.api as sm
from pyxll import xl_func

from ._coerce import safe_err, to_1d_floats


@xl_func(
    "float reserves_usd, float short_term_debt, float monthly_imports,"
    " float broad_money, float gdp: object[][]",
    name="SOV_RESERVES_ADEQUACY",
)
def reserves_adequacy_metrics(
    reserves_usd: float,
    short_term_debt: float,
    monthly_imports: float,
    broad_money: float,
    gdp: float,
) -> list[list[Any]] | str:
    """Dashboard of standard reserve adequacy metrics.

    Returns:
    - import_cover_months    : reserves / monthly imports
    - greenspan_guidotti     : reserves / short-term debt  (target ≥ 1.0)
    - wijnholds_kapteyn      : reserves / broad money
    - imf_ara_composite      : reserves / IMF ARA benchmark
      (simplified: 30 % STD + 60 % annual imports + 10 % M2)
    """
    try:
        R = float(reserves_usd)
        std = float(short_term_debt)
        mi = float(monthly_imports)
        m2 = float(broad_money)
        if R < 0:
            return safe_err(ValueError("reserves_usd must be >= 0"))
        import_cover = R / mi if mi > 0 else float("nan")
        greenspan = R / std if std > 0 else float("nan")
        wk = R / m2 if m2 > 0 else float("nan")
        # IMF ARA composite (simplified fixed-weight benchmark)
        ara_benchmark = 0.30 * std + 0.60 * (mi * 12) + 0.10 * m2
        ara_ratio = R / ara_benchmark if ara_benchmark > 0 else float("nan")
        return [
            ["metric", "value"],
            ["import_cover_months", round(import_cover, 4)],
            ["greenspan_guidotti", round(greenspan, 4)],
            ["wijnholds_kapteyn", round(wk, 4)],
            ["imf_ara_composite", round(ara_ratio, 4)],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float current_account, float fdi, float portfolio_flows,"
    " float debt_amortization, float reserves: float",
    name="SOV_BOP_FINANCING_GAP",
)
def bop_financing_gap(
    current_account: float,
    fdi: float,
    portfolio_flows: float,
    debt_amortization: float,
    reserves: float,
) -> float | str:
    """Residual BoP financing need (a positive result means a gap exists).

    gap = debt_amortization - (current_account + fdi + portfolio_flows + reserves)
    """
    try:
        gap = float(debt_amortization) - (
            float(current_account) + float(fdi) + float(portfolio_flows) + float(reserves)
        )
        return round(float(gap), 6)
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float reer_index, float[] reer_history, float[] terms_of_trade, float[] nfa_gdp: object[][]",
    name="SOV_FX_MISALIGNMENT",
)
def exchange_rate_misalignment(
    reer_index: float,
    reer_history: Any,
    terms_of_trade: Any,
    nfa_gdp: Any,
) -> list[list[Any]] | str:
    """Estimate REER over/undervaluation using a BEER (Behavioural Equilibrium
    Exchange Rate) regression.

    Regresses historical REER on terms of trade and NFA/GDP, then evaluates
    the fitted equilibrium at the most recent observations.  A positive
    misalignment means the currency appears overvalued.
    """
    try:
        reer_h = np.array(to_1d_floats(reer_history), dtype=float)
        tot = np.array(to_1d_floats(terms_of_trade), dtype=float)
        nfa = np.array(to_1d_floats(nfa_gdp), dtype=float)
        n = len(reer_h)
        if n < 3:
            return safe_err(ValueError("Need at least 3 observations"))
        if len(tot) != n or len(nfa) != n:
            return safe_err(ValueError("All series must have the same length"))
        X = np.column_stack([tot, nfa])
        X = sm.add_constant(X)
        model = sm.OLS(reer_h, X).fit()
        x_current = np.array([1.0, tot[-1], nfa[-1]])
        reer_eq = float(model.predict(x_current)[0])
        misalignment = float(reer_index) - reer_eq
        pct_misalignment = (misalignment / reer_eq * 100.0) if reer_eq != 0 else float("nan")
        return [
            ["metric", "value"],
            ["reer_observed", round(float(reer_index), 4)],
            ["reer_equilibrium", round(reer_eq, 4)],
            ["misalignment", round(misalignment, 4)],
            ["misalignment_pct", round(pct_misalignment, 4)],
            ["R2", round(float(model.rsquared), 4)],
        ]
    except Exception as e:
        return safe_err(e)

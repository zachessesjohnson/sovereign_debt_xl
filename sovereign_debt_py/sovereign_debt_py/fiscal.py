from __future__ import annotations

from typing import Any

import numpy as np
import statsmodels.api as sm

from ._coerce import safe_err, to_1d_floats


def debt_trajectory_forecast(
    gdp_growth_path: Any,
    primary_balance_path: Any,
    interest_rate_path: Any,
    initial_debt_gdp: float,
    years: int,
) -> list[list[Any]] | str:
    """Project debt-to-GDP forward using the standard debt dynamics equation.

    d_t = d_{t-1} * (1+r) / (1+g) - pb_t
    """
    try:
        g = to_1d_floats(gdp_growth_path)
        pb = to_1d_floats(primary_balance_path)
        r = to_1d_floats(interest_rate_path)
        if years <= 0:
            return safe_err(ValueError("years must be > 0"))
        if len(g) < years or len(pb) < years or len(r) < years:
            return safe_err(ValueError("paths must each have at least 'years' elements"))
        out: list[list[Any]] = [["year", "debt_gdp"]]
        d = float(initial_debt_gdp)
        for t in range(years):
            if (1.0 + g[t]) == 0:
                return safe_err(ValueError(f"1 + gdp_growth is zero at period {t + 1}"))
            d = d * (1.0 + r[t]) / (1.0 + g[t]) - pb[t]
            out.append([t + 1, round(d, 6)])
        return out
    except Exception as e:
        return safe_err(e)


def fiscal_reaction_function(
    primary_balance_history: Any,
    debt_gdp_history: Any,
    output_gap_history: Any,
) -> list[list[Any]] | str:
    """Estimate Bohn (1998) fiscal reaction function via OLS."""
    try:
        pb = np.array(to_1d_floats(primary_balance_history), dtype=float)
        d = np.array(to_1d_floats(debt_gdp_history), dtype=float)
        og = np.array(to_1d_floats(output_gap_history), dtype=float)
        n = len(pb)
        if n < 4:
            return safe_err(ValueError("Need at least 4 observations"))
        if len(d) != n or len(og) != n:
            return safe_err(ValueError("All series must have the same length"))
        y = pb[1:]
        X = np.column_stack([d[:-1], og[1:]])
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        params = model.params.tolist()
        pvals = model.pvalues.tolist()
        out: list[list[Any]] = [["term", "coef", "pvalue"]]
        out.append(["const", round(float(params[0]), 6), round(float(pvals[0]), 6)])
        out.append(["lagged_debt", round(float(params[1]), 6), round(float(pvals[1]), 6)])
        out.append(["output_gap", round(float(params[2]), 6), round(float(pvals[2]), 6)])
        out.append(["R2", round(float(model.rsquared), 6), float("nan")])
        return out
    except Exception as e:
        return safe_err(e)


def implicit_interest_rate(
    interest_payments: float,
    avg_debt_stock_start: float,
    avg_debt_stock_end: float,
) -> float | str:
    """Effective cost of the debt portfolio (implicit interest rate)."""
    try:
        avg_stock = (float(avg_debt_stock_start) + float(avg_debt_stock_end)) / 2.0
        if avg_stock == 0:
            return safe_err(ValueError("Average debt stock is zero"))
        return round(float(interest_payments) / avg_stock, 6)
    except Exception as e:
        return safe_err(e)


def debt_stabilizing_primary_balance(
    debt_gdp: float,
    real_interest_rate: float,
    real_gdp_growth: float,
) -> float | str:
    """Primary balance needed to hold debt-to-GDP constant."""
    try:
        d = float(debt_gdp)
        r = float(real_interest_rate)
        g = float(real_gdp_growth)
        if (1.0 + g) == 0:
            return safe_err(ValueError("1 + real_gdp_growth is zero"))
        return round(d * (r - g) / (1.0 + g), 6)
    except Exception as e:
        return safe_err(e)

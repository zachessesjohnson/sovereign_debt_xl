from __future__ import annotations

import math
from typing import Any

import numpy as np
import statsmodels.api as sm
from pyxll import xl_func
from scipy import stats

from ._coerce import safe_err, to_1d_floats


@xl_func(
    "float debt_face_value, float asset_value, float asset_volatility,"
    " float risk_free_rate, float maturity: object[][]",
    name="SOV_MERTON_DEFAULT_PROB",
)
def merton_sovereign_default_prob(
    debt_face_value: float,
    asset_value: float,
    asset_volatility: float,
    risk_free_rate: float,
    maturity: float,
) -> list[list[Any]] | str:
    """Merton structural model adapted for sovereigns.

    Returns d1, d2 (distance-to-default), and the risk-neutral default probability.
    """
    try:
        F = float(debt_face_value)
        V = float(asset_value)
        sigma = float(asset_volatility)
        r = float(risk_free_rate)
        T = float(maturity)
        if V <= 0 or sigma <= 0 or T <= 0 or F <= 0:
            return safe_err(ValueError("All inputs must be positive"))
        d1 = (math.log(V / F) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        default_prob = float(stats.norm.cdf(-d2))
        return [
            ["metric", "value"],
            ["d1", round(d1, 6)],
            ["d2_distance_to_default", round(d2, 6)],
            ["default_probability", round(default_prob, 6)],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float cds_spread_bps, float recovery_rate, float tenor_years: object[][]",
    name="SOV_CDS_DEFAULT_PROB",
)
def cds_implied_default_prob(
    cds_spread_bps: float,
    recovery_rate: float,
    tenor_years: float,
) -> list[list[Any]] | str:
    """Back out cumulative and annualized risk-neutral default probability from CDS spread.

    Uses the standard hazard-rate approximation: lambda = spread / LGD.
    """
    try:
        s = float(cds_spread_bps) / 10_000.0  # bps → decimal
        R = float(recovery_rate)
        T = float(tenor_years)
        if T <= 0:
            return safe_err(ValueError("tenor_years must be > 0"))
        if not (0.0 <= R < 1.0):
            return safe_err(ValueError("recovery_rate must be in [0, 1)"))
        lgd = 1.0 - R
        hazard = s / lgd
        cum_pd = 1.0 - math.exp(-hazard * T)
        annual_pd = 1.0 - math.exp(-hazard)
        return [
            ["metric", "value"],
            ["hazard_rate", round(hazard, 6)],
            ["cumulative_pd", round(cum_pd, 6)],
            ["annual_pd", round(annual_pd, 6)],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float current_account_gdp, float reserves_imports, float debt_gdp,"
    " float gdp_growth, float inflation: object[][]",
    name="SOV_ZSCORE_SOVEREIGN",
)
def zscore_sovereign(
    current_account_gdp: float,
    reserves_imports: float,
    debt_gdp: float,
    gdp_growth: float,
    inflation: float,
) -> list[list[Any]] | str:
    """Composite early-warning scoring model inspired by Reinhart/Rogoff indicators.

    Standardises each indicator against approximate historical benchmarks and
    returns a composite z-score plus its percentile rank.
    """
    try:
        # (name, value, direction) — direction=+1 means higher value → more risk
        indicators = [
            ("current_account_gdp", float(current_account_gdp), -1.0),
            ("reserves_imports", float(reserves_imports), -1.0),
            ("debt_gdp", float(debt_gdp), +1.0),
            ("gdp_growth", float(gdp_growth), -1.0),
            ("inflation", float(inflation), +1.0),
        ]
        # Approximate historical (mean, std) benchmarks for standardisation
        benchmarks = {
            "current_account_gdp": (-0.03, 0.05),
            "reserves_imports": (4.0, 3.0),
            "debt_gdp": (0.60, 0.30),
            "gdp_growth": (0.03, 0.03),
            "inflation": (0.05, 0.08),
        }
        z_components: list[float] = []
        for name, val, direction in indicators:
            mean, std = benchmarks[name]
            z = (val - mean) / std * direction
            z_components.append(z)
        composite_z = float(np.mean(z_components))
        percentile = float(stats.norm.cdf(composite_z) * 100.0)
        out: list[list[Any]] = [["metric", "value"]]
        for (name, _, _), z in zip(indicators, z_components):
            out.append([f"z_{name}", round(z, 4)])
        out.append(["composite_zscore", round(composite_z, 4)])
        out.append(["percentile_rank", round(percentile, 2)])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[] embi_spread, float[] us_vix, float[] us_10y,"
    " float[] commodity_index, float[] country_fundamentals: object[][]",
    name="SOV_SPREAD_DECOMPOSITION",
)
def spread_decomposition(
    embi_spread: Any,
    us_vix: Any,
    us_10y: Any,
    commodity_index: Any,
    country_fundamentals: Any,
) -> list[list[Any]] | str:
    """Decompose sovereign spreads into global risk factors vs. idiosyncratic fundamentals.

    Runs OLS of EMBI spread on (VIX, US 10y, commodity index) as global factors and
    a country-fundamentals composite as the idiosyncratic factor.  Returns coefficients,
    p-values, R², and the share of fitted variance attributable to each group.
    """
    try:
        y = np.array(to_1d_floats(embi_spread), dtype=float)
        vix = np.array(to_1d_floats(us_vix), dtype=float)
        usy = np.array(to_1d_floats(us_10y), dtype=float)
        comm = np.array(to_1d_floats(commodity_index), dtype=float)
        fund = np.array(to_1d_floats(country_fundamentals), dtype=float)
        n = len(y)
        if n < 5:
            return safe_err(ValueError("Need at least 5 observations"))
        for arr, lbl in [
            (vix, "us_vix"),
            (usy, "us_10y"),
            (comm, "commodity_index"),
            (fund, "country_fundamentals"),
        ]:
            if len(arr) != n:
                return safe_err(ValueError(f"{lbl} must have the same length as embi_spread"))
        X = np.column_stack([vix, usy, comm, fund])
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        params = model.params.tolist()
        pvals = model.pvalues.tolist()
        # Share of fitted variance from global (cols 1-3) vs. idiosyncratic (col 4)
        global_fitted = X[:, 1:4] @ np.array(params[1:4])
        idio_fitted = X[:, 4] * params[4]
        global_ss = float(np.var(global_fitted))
        idio_ss = float(np.var(idio_fitted))
        denom = global_ss + idio_ss if (global_ss + idio_ss) > 0 else 1.0
        labels = ["const", "us_vix", "us_10y", "commodity_index", "country_fundamentals"]
        out: list[list[Any]] = [["term", "coef", "pvalue"]]
        for lbl, coef, pval in zip(labels, params, pvals):
            out.append([lbl, round(float(coef), 6), round(float(pval), 6)])
        out.append(["R2", round(float(model.rsquared), 6), float("nan")])
        out.append(["global_share", round(global_ss / denom, 4), float("nan")])
        out.append(["idiosyncratic_share", round(idio_ss / denom, 4), float("nan")])
        return out
    except Exception as e:
        return safe_err(e)

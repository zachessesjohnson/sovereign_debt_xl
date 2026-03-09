from __future__ import annotations

from typing import Any

import numpy as np
from pyxll import xl_func

from ._coerce import safe_err, to_1d_floats


@xl_func(
    "float[] base_case_params, float[] shock_distributions, int num_simulations, int years: object[][]",
    name="SOV_FAN_CHART_DEBT",
)
def fan_chart_debt(
    base_case_params: Any,
    shock_distributions: Any,
    num_simulations: int,
    years: int,
) -> list[list[Any]] | str:
    """Monte Carlo debt fan chart — shocks GDP growth, interest rate, and primary balance.

    base_case_params  : [gdp_growth, interest_rate, primary_balance, initial_debt_gdp]
    shock_distributions: [gdp_growth_std, interest_rate_std, primary_balance_std]

    Returns percentile paths (P10/P25/P50/P75/P90) of debt-to-GDP by year.
    """
    try:
        bp = to_1d_floats(base_case_params)
        sd = to_1d_floats(shock_distributions)
        if len(bp) < 4:
            return safe_err(
                ValueError(
                    "base_case_params needs 4 values: "
                    "[gdp_growth, interest_rate, primary_balance, initial_debt_gdp]"
                )
            )
        if len(sd) < 3:
            return safe_err(
                ValueError(
                    "shock_distributions needs 3 values: "
                    "[gdp_growth_std, interest_rate_std, primary_balance_std]"
                )
            )
        if num_simulations <= 0 or years <= 0:
            return safe_err(ValueError("num_simulations and years must be > 0"))
        g0, r0, pb0, d0 = bp[0], bp[1], bp[2], bp[3]
        sg, sr, spb = sd[0], sd[1], sd[2]
        rng = np.random.default_rng(42)
        paths = np.zeros((num_simulations, years))
        for sim in range(num_simulations):
            d = d0
            for t in range(years):
                g = g0 + rng.normal(0.0, sg)
                r = r0 + rng.normal(0.0, sr)
                pb = pb0 + rng.normal(0.0, spb)
                denom = 1.0 + g
                d = d * (1.0 + r) / denom - pb if denom != 0 else d
                paths[sim, t] = d
        out: list[list[Any]] = [["year", "p10", "p25", "p50", "p75", "p90"]]
        for t in range(years):
            col = paths[:, t]
            p10, p25, p50, p75, p90 = np.percentile(col, [10, 25, 50, 75, 90]).tolist()
            out.append(
                [t + 1, round(p10, 4), round(p25, 4), round(p50, 4), round(p75, 4), round(p90, 4)]
            )
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float debt_gdp, float banking_sector_assets_gdp, float soe_debt_gdp,"
    " float historical_realization_rate: object[][]",
    name="SOV_CONTINGENT_LIABILITY_SHOCK",
)
def contingent_liability_shock(
    debt_gdp: float,
    banking_sector_assets_gdp: float,
    soe_debt_gdp: float,
    historical_realization_rate: float,
) -> list[list[Any]] | str:
    """Estimate the debt impact of crystallising contingent liabilities.

    Applies a historical realization rate to banking-sector assets and SOE debt
    to estimate the potential public-sector absorption.
    """
    try:
        d = float(debt_gdp)
        banking = float(banking_sector_assets_gdp)
        soe = float(soe_debt_gdp)
        rate = float(historical_realization_rate)
        if not (0.0 <= rate <= 1.0):
            return safe_err(ValueError("historical_realization_rate must be in [0, 1]"))
        banking_shock = banking * rate
        soe_shock = soe * rate
        total_shock = banking_shock + soe_shock
        new_debt = d + total_shock
        return [
            ["metric", "value"],
            ["initial_debt_gdp", round(d, 4)],
            ["banking_shock_gdp", round(banking_shock, 4)],
            ["soe_shock_gdp", round(soe_shock, 4)],
            ["total_contingent_shock_gdp", round(total_shock, 4)],
            ["post_shock_debt_gdp", round(new_debt, 4)],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float fx_denominated_share, float debt_gdp, float depreciation_pct: float",
    name="SOV_FX_PASSTHROUGH_DEBT",
)
def exchange_rate_passthrough_to_debt(
    fx_denominated_share: float,
    debt_gdp: float,
    depreciation_pct: float,
) -> float | str:
    """Mechanical increase in debt-to-GDP from a currency depreciation.

    increase = fx_share × debt_gdp × depreciation_pct
    """
    try:
        share = float(fx_denominated_share)
        d = float(debt_gdp)
        dep = float(depreciation_pct)
        if not (0.0 <= share <= 1.0):
            return safe_err(ValueError("fx_denominated_share must be in [0, 1]"))
        return round(share * d * dep, 6)
    except Exception as e:
        return safe_err(e)

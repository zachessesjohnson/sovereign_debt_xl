from __future__ import annotations

import math
from typing import Any

import numpy as np
from pyxll import xl_func
from scipy.optimize import brentq, minimize

from ._coerce import safe_err, to_1d_floats


def _ns_yields(params: list[float], t: np.ndarray) -> np.ndarray:
    """Nelson-Siegel yield formula (vectorised)."""
    b0, b1, b2, tau = params
    tau = max(float(tau), 1e-6)
    x = t / tau
    # Limit of (1 - e^-x)/x as x -> 0 is 1
    loading = np.where(x < 1e-10, 1.0, (1.0 - np.exp(-x)) / x)
    return b0 + b1 * loading + b2 * (loading - np.exp(-x))


@xl_func(
    "float[] maturities, float[] yields: object[][]",
    name="SOV_NELSON_SIEGEL",
)
def nelson_siegel_fit(maturities: Any, yields: Any) -> list[list[Any]] | str:
    """Fit the Nelson-Siegel model to a sovereign yield curve.

    Returns level (β0), slope (β1), curvature (β2), decay (τ) parameters,
    fitting RMSE, and fitted yields at each input maturity.
    """
    try:
        m = np.array(to_1d_floats(maturities), dtype=float)
        y = np.array(to_1d_floats(yields), dtype=float)
        if len(m) < 3 or len(y) < 3:
            return safe_err(ValueError("Need at least 3 maturity/yield pairs"))
        if len(m) != len(y):
            return safe_err(ValueError("maturities and yields must have the same length"))
        if np.any(m <= 0):
            return safe_err(ValueError("All maturities must be positive"))

        def objective(params: list[float]) -> float:
            return float(np.sum((_ns_yields(params, m) - y) ** 2))

        x0 = [float(np.mean(y)), -0.01, 0.01, 2.0]
        bounds = [(None, None), (None, None), (None, None), (0.01, 30.0)]
        res = minimize(objective, x0, method="L-BFGS-B", bounds=bounds)
        b0, b1, b2, tau = res.x.tolist()
        fitted = _ns_yields(res.x, m).tolist()
        rmse = float(np.sqrt(np.mean((y - np.array(fitted)) ** 2)))
        out: list[list[Any]] = [
            ["metric", "value"],
            ["beta0_level", round(b0, 6)],
            ["beta1_slope", round(b1, 6)],
            ["beta2_curvature", round(b2, 6)],
            ["tau", round(tau, 6)],
            ["rmse", round(rmse, 6)],
            ["", ""],
            ["maturity", "fitted_yield"],
        ]
        for mi, fi in zip(m.tolist(), fitted):
            out.append([round(mi, 4), round(fi, 6)])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float bond_price, float coupon, float maturity,"
    " float[] benchmark_curve_tenors, float[] benchmark_curve_rates: float",
    name="SOV_ZSPREAD",
)
def zspread(
    bond_price: float,
    coupon: float,
    maturity: float,
    benchmark_curve_tenors: Any,
    benchmark_curve_rates: Any,
) -> float | str:
    """Z-spread of a sovereign bond over a benchmark curve (annual, continuous discounting).

    Finds the constant spread z added to the interpolated benchmark rate at each
    cash-flow date such that the discounted cash flows equal bond_price.
    Face value is assumed to be 100; coupon is the annual cash amount.
    """
    try:
        price = float(bond_price)
        c = float(coupon)
        T = float(maturity)
        tenors = np.array(to_1d_floats(benchmark_curve_tenors), dtype=float)
        rates = np.array(to_1d_floats(benchmark_curve_rates), dtype=float)
        if len(tenors) < 2 or len(tenors) != len(rates):
            return safe_err(ValueError("Need at least 2 matched benchmark tenor/rate pairs"))
        if T <= 0 or price <= 0:
            return safe_err(ValueError("maturity and bond_price must be > 0"))
        periods = max(1, int(round(T)))

        def pv_at_spread(z: float) -> float:
            total = 0.0
            for t in range(1, periods + 1):
                r_bench = float(np.interp(float(t), tenors, rates))
                cf = c + (100.0 if t == periods else 0.0)
                total += cf * math.exp(-(r_bench + z) * t)
            return total

        def obj(z: float) -> float:
            return pv_at_spread(z) - price

        try:
            z = brentq(obj, -0.5, 2.0, xtol=1e-8)
        except ValueError:
            return safe_err(ValueError("Could not find z-spread in [-50%, +200%] range"))
        return round(float(z), 6)
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float bond_tenor, float[] yield_curve_tenors, float[] yield_curve_rates, int horizon_months: object[][]",
    name="SOV_CARRY_ROLLDOWN",
)
def carry_rolldown(
    bond_tenor: float,
    yield_curve_tenors: Any,
    yield_curve_rates: Any,
    horizon_months: int,
) -> list[list[Any]] | str:
    """Expected carry and rolldown return assuming an unchanged yield curve.

    Carry  = coupon income earned over the horizon.
    Rolldown = price gain from the bond rolling to a lower-tenor (typically lower-yield)
               point on the curve, approximated via modified duration.
    """
    try:
        tenor = float(bond_tenor)
        tenors = np.array(to_1d_floats(yield_curve_tenors), dtype=float)
        rates = np.array(to_1d_floats(yield_curve_rates), dtype=float)
        if len(tenors) < 2 or len(tenors) != len(rates):
            return safe_err(ValueError("Need at least 2 matched tenor/rate pairs"))
        if tenor <= 0 or horizon_months <= 0:
            return safe_err(ValueError("bond_tenor and horizon_months must be > 0"))
        h = float(horizon_months) / 12.0
        y0 = float(np.interp(tenor, tenors, rates))
        rolled_tenor = max(tenor - h, float(tenors[0]))
        y1 = float(np.interp(rolled_tenor, tenors, rates))
        # Approximate modified duration
        dur = tenor / (1.0 + y0)
        carry = y0 * h
        rolldown = -dur * (y1 - y0)
        total_return = carry + rolldown
        return [
            ["metric", "value"],
            ["initial_yield", round(y0, 6)],
            ["rolled_yield", round(y1, 6)],
            ["carry", round(carry, 6)],
            ["rolldown", round(rolldown, 6)],
            ["total_return", round(total_return, 6)],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float bond_price, float coupon, float maturity,"
    " float[] ois_curve_tenors, float[] ois_curve_rates: float",
    name="SOV_ASW_SPREAD",
)
def asw_spread(
    bond_price: float,
    coupon: float,
    maturity: float,
    ois_curve_tenors: Any,
    ois_curve_rates: Any,
) -> float | str:
    """Asset-swap spread (ASW) of a bond over the OIS curve.

    ASW = (PV_fixed_at_OIS - price) / OIS_annuity
    where PV_fixed discounts bond cash flows at OIS rates and the annuity is the
    sum of OIS discount factors over the bond's life.
    Face value is assumed to be 100; coupon is the annual cash amount.
    """
    try:
        price = float(bond_price)
        c = float(coupon)
        T = float(maturity)
        tenors = np.array(to_1d_floats(ois_curve_tenors), dtype=float)
        rates = np.array(to_1d_floats(ois_curve_rates), dtype=float)
        if len(tenors) < 2 or len(tenors) != len(rates):
            return safe_err(ValueError("Need at least 2 matched OIS tenor/rate pairs"))
        if T <= 0:
            return safe_err(ValueError("maturity must be > 0"))
        periods = max(1, int(round(T)))
        pv_fixed = 0.0
        annuity = 0.0
        for t in range(1, periods + 1):
            r_ois = float(np.interp(float(t), tenors, rates))
            df = math.exp(-r_ois * t)
            pv_fixed += c * df
            annuity += df
        # Add principal repayment at maturity
        r_T = float(np.interp(T, tenors, rates))
        pv_fixed += 100.0 * math.exp(-r_T * T)
        if annuity == 0:
            return safe_err(ValueError("OIS annuity is zero"))
        return round((pv_fixed - price) / annuity, 6)
    except Exception as e:
        return safe_err(e)
